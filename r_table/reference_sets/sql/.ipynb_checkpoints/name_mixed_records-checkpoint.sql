create view name_records as 
select * from articles_2_ab
order by random()
limit 150000;