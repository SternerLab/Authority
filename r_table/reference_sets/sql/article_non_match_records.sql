create view article_nm_records as 
select * from articles 
order by random()
limit 100000;