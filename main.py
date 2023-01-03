from datetime import datetime
import xml.dom.minidom
import pytz
from feedgen.feed import FeedGenerator
import requests
import ke

# Need to use a file for persistence in case old episodes drop off Kan-Yiddish Webpage
dates_and_mp3_urls_file = "dates_and_mp3_urls.txt"


def download_data_for_rss():
    def get_episodes_from_main_kanyiddish_page():
        main_kan_yiddish_page = (
            "https://www.kan.org.il/radio/program.aspx/?progId=1136 "
        )
        main_page_s = str(requests.get(main_kan_yiddish_page).content)
        podcast_url_base = "https://omny.fm/shows/kan-yiddish/"
        embed_path = "/embed"
        episode_matches = ke.finditer(
            '[["'
            + podcast_url_base
            + '"] [capture:date 0+ [#digit | "-"]] ["'
            + embed_path
            + '"]]',
            main_page_s,
        )
        return episode_matches

    def extract_date_and_mp3_url_from_episode_page(date_orig, episode_url):
        def extract_date(date_orig):

            date_parts = date_orig.split("-")
            if len(date_parts) == 2:
                day, month = date_parts
                year = "2022"
            else:
                assert len(date_parts) == 3
                day, month, year = date_parts
                if len(str(year)) == 2:
                    year = "20" + year
            year, month, day = int(year), int(month), int(day)
            return f"{year}-{month:02d}-{day:02d}"

        date_s = extract_date(date_orig)

        episode_s = str(requests.get(episode_url).content)
        match_mp3 = ke.findall(
            '["https://traffic.omny.fm/d/clips/" [1+ #any]  "mp3"]', episode_s
        )
        assert len(match_mp3) == 1
        return date_s, match_mp3[0]

    episode_matches = get_episodes_from_main_kanyiddish_page()
    date_and_mp3_urls = [
        extract_date_and_mp3_url_from_episode_page(
            episode_match.group("date"), episode_match.group()
        )
        for episode_match in episode_matches
    ]

    date_and_mp3_urls = existing_and_new_date_and_url_pairs(date_and_mp3_urls)
    lines = [
        f"{date_and_mp3_url[0]},{date_and_mp3_url[1]}\n"
        for date_and_mp3_url in date_and_mp3_urls
    ]
    with open(dates_and_mp3_urls_file, "w") as f_out:
        f_out.writelines(lines)


def existing_and_new_date_and_url_pairs(date_and_mp3_urls):
    try:
        with open(dates_and_mp3_urls_file) as f:
            existing_pairs_with_newline = [line.split(",") for line in f.readlines()]
            existing_pairs = [
                (p[0], p[1].rstrip()) for p in existing_pairs_with_newline
            ]
    except FileNotFoundError:
        existing_pairs = []

    all_pairs = date_and_mp3_urls + existing_pairs

    # Do not duplicate mp3s
    mp3_to_date = {mp3: date for (mp3, date) in all_pairs}
    ret = [(date, mp3) for date, mp3 in mp3_to_date.items()]

    return sorted(ret)


def to_rss():
    with open(dates_and_mp3_urls_file) as f:
        fg = build_feed(f.readlines())
        rss = fg.rss_str()
        podcast_xml = xml.dom.minidom.parseString(rss).toprettyxml(
            indent="  ",
        )

    with open("docs/podcast.xml", "w") as xml_out:
        xml_out.write(podcast_xml)


def build_feed(lines):
    def build_feed_gen():
        fg = FeedGenerator()
        fg.load_extension("podcast")
        fg.title("Kan Yiddish")
        fg.description("Kan Yiddish")
        fg.link(
            href="https://www.kan.org.il/radio/program.aspx/?progid=1136",
            rel="alternate",
        )
        fg.podcast.itunes_category("Culture", "Yiddish")
        return fg

    def append_feed_item(date, url, fg):
        fe = fg.add_entry()
        fe.id(url)
        fe.published(date)
        fe.title("Kan Yiddish " + date.strftime("%Y-%m-%d"))
        fe.enclosure(url, 0, "audio/mpeg")

    assert sorted(lines) == lines
    fg = build_feed_gen()

    for line in lines:
        assert line.count(",") == 1, f"line was {line }"
        date_s, url = line.split(",")
        date = pytz.timezone("Israel").localize(datetime.strptime(date_s, "%Y-%m-%d"))
        append_feed_item(date, url, fg)
    return fg


if __name__ == "__main__":
    download_data_for_rss()
    to_rss()
