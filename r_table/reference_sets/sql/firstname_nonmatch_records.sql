create view firstname_nm_records as 
select * from articles_2_ab
order by random()
limit 3000;