create view firstname_m_records as 
select * from articles_2_ab
order by random()
limit 300;