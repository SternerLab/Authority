create view article_nm_records as 
select * from articles_2_ab 
order by random()
limit 100000;