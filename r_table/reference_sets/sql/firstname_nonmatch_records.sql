create view firstname_nm_records as 
select * from articles
order by random()
limit 30000;