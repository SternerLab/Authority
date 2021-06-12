create view name_records as 
select * from articles
order by random()
limit 700000;