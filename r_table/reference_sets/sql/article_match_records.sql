create view article_m_records as 
select * from articles
order by random()
limit 600000;