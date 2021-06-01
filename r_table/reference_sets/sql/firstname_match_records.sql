create view firstname_m_records as 
select * from articles
order by random()
limit 300;