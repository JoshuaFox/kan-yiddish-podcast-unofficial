from datetime import datetime

import pytz
from feedgen.feed import FeedGenerator


def to_rss(name):
   fg = FeedGenerator()
   fg.load_extension('podcast')
   fg.title("Kan Yiddish")
   fg.description("Kan Yiddish")
   fg.link(href="https://www.kan.org.il/radio/program.aspx/?progid=1136", rel="alternate")
   fg.podcast.itunes_category('Culture', 'Yiddish')


   with open("dates_and_mp3_urls.txt") as f:
        lines=f.readlines()
        for l in lines:
            date_s, url=l.split(",")
            date_no_tz=datetime.strptime(date_s, "%d-%m-%Y" )
            timezone = pytz.timezone("Israel")
            date = timezone.localize(date_no_tz)
            iso_date_s=datetime.strftime(date,  "%Y-%m-%d")
            fe = fg.add_entry()
            fe.id(url)
            fe.published(date)
            fe.title("Kan Yiddish "+iso_date_s)

            #fe.description('Enjoy our first episode.')
            fe.enclosure(url, 0, 'audio/mpeg')
   # fg.rss_str(pretty=True)
   fg.rss_file('podcast.xml', pretty=True)


if __name__ == '__main__':
      to_rss('PyCharm')

