 
set -x
set -e
set -u

#rm dates_and_mp3_urls.txt | true
#rm audio_player_urls.lst |true
#rm *.mp3  |true

curl https://www.kan.org.il/radio/program.aspx/?progId=1136  | perl -ne 'm/(https:\/\/omny.fm\/shows\/kan-yiddish\/.*\/embed)/  && print "$1\n"' >audio_player_urls.lst

cat audio_player_urls.lst | while read line 
do
	 # Line like https://omny.fm/shows/kan-yiddish/9-12-22/embed
	 date_base=$(echo $line |perl -ne 'm/https:\/\/omny.fm\/shows\/kan-yiddish\/([0-9-]+)\/embed/  && print "$1\n"' )
	if [[ $date_base == *22 ]]
	then
	    if [[ $date_base == *-22 ]]
	    then
	      date_base="${date_base%???}-2022"
	    else
	      true # no op
        fi
    else
		date_base="${date_base}-2022"
    fi
	 mp3_url=$( curl $line  | perl -ne 'm/(https:\/\/traffic.omny.fm\/d\/clips\/.*mp3)/  && print "$1\n"' )	 
	 [ -z "${mp3_url}" ] && exit 1
	 echo "${date_base},${mp3_url}" >> dates_and_mp3_urls.txt
	 #curl -L -o ${date_base}.mp3 ${mp3_url}

done

sort  dates_and_mp3_urls.txt | uniq > temp; mv temp dates_and_mp3_urls.txt

rm audio_player_urls.lst