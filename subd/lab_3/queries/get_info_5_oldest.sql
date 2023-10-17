
select * from (select * from farm.farm_schema.cows
order by birth_date
fetch first 5 rows only) cows
join get_cow_info(cows.cow_name) cow_info on cow_info.cow_name = cows.cow_name