alter view name_set as 
select tb1.id as id1, tb1.position as position1, tb1.last_name as last_name1, tb1.first_initial as first_initial1, tb1.middle_initial as middle_initial1, 
tb1.suffix as suffix1, tb1.title as title1, tb1.journal_name as journal_name1, tb1.first_name as first_name1, tb1.middle_name as middle_name1, tb1.fullname as fullname1, tb1.authors as authors1 ,tb1.language as language1,
tb2.id as id2, tb2.position as position2, tb2.last_name as last_name2, tb2.first_initial as first_initial2, tb2.middle_initial as middle_initial2, 
tb2.suffix as suffix2, tb2.title as title2, tb2.journal_name as journal_name2, tb2.first_name as first_name2, tb2.middle_name as middle_name2, tb2.fullname as fullname2, tb2.authors as authors2 ,tb2.language as language2,
'False' as iscomputed 
from articles as tb1 INNER JOIN articles as tb2
on tb1.id != tb2.id and tb1.id < tb2.id and tb1.first_initial = tb2.first_initial and tb1.position = 1 and tb2.position = 1 and tb1.last_name = tb2.last_name
where not tb1.first_initial = '' and not tb2.first_initial = ''
and length(tb1.middle_name)-length(REPLACE(tb1.middle_name,' ', '')) < 1
and length(tb2.middle_name)-length(REPLACE(tb2.middle_name,' ', '')) < 1;