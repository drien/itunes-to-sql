-- Get non-smart playlists ordered by the number of tracks they contain

select
    count(*) as number_of_tracks,
    playlists.name
from playlists
    left join playlist_items on playlists.playlist_id = playlist_items.playlist_id
where playlists.smart_criteria is null
group by playlists.playlist_id, playlists.name
order by number_of_tracks desc
limit 50;
