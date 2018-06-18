-- Count the number of tracks by star rating

select
    case
        when rating = 20 then '*'
        when rating = 40 then '* *'
        when rating = 60 then '* * *'
        when rating = 80 then '* * * *'
        when rating = 100 then '* * * * *'
    end as stars,
    count(*) as count
from tracks
group by rating;
