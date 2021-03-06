-- Like the artist_plays query, gets the total number of plays per album

select
    artist,
    album,
    sum(play_count) as total_plays,
    max(play_count) as most_played_count,
    round(avg(play_count)) as average_count,
    min(play_count) as least_played_count
from tracks
group by artist, album
order by total_plays desc
limit 50;
