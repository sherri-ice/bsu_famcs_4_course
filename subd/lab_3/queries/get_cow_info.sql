CREATE FUNCTION get_cow_info(IN q_cow_name TEXT)
    RETURNS TABLE
            (
                cow_name             TEXT,
                gender               gender,
                birth_date           DATE,
                is_active            BOOLEAN,
                remove_date          DATE,
                barn_id              INT,
                place_id             INT,
                last_milk_date       DATE,
                last_diet_details    TEXT,
                last_diet_start_date DATE,
                last_diet_end_date   DATE,
                last_massage_date    DATE,
                vaccinations_list    TEXT
            )
LANGUAGE plpgsql
AS
$$
BEGIN
    RETURN QUERY
        SELECT c.cow_name,
               c.gender,
               c.birth_date,
               c.is_active,
               c.remove_date,
               c.barn_id,
               c.place_id,
               fmp.milk_date      AS last_milk_date,
               diets.diet_details AS last_diet_details,
               fdc.start_date     AS last_diet_start_date,
               fdc.end_date       AS last_diet_end_date,
               fm.date            AS last_massage_date,
               vac.vaccinations_list
        FROM farm_schema.cows c
                 INNER JOIN farm_schema.f_milk_production fmp ON c.cow_id = fmp.cow_id
                 INNER JOIN (SELECT cow_id,
                                    string_agg(v.vaccination_name, ', ') AS vaccinations_list
                             FROM farm_schema.f_vaccinations fv
                                      INNER JOIN farm_schema.vaccinations v ON fv.vaccination_id = v.vaccination_type
                             GROUP BY cow_id) vac ON vac.cow_id = c.cow_id
                 LEFT JOIN farm_schema.f_diets_cows fdc
                           ON c.cow_id = fdc.cow_id
                 LEFT JOIN farm_schema.diets diets ON fdc.diet_id = diets.diet_id
                 LEFT JOIN farm_schema.f_massage fm ON c.cow_id = fm.cow_id
        WHERE c.cow_name = q_cow_name
        ORDER BY last_diet_start_date,
                 last_diet_end_date,
                 last_massage_date,
                 last_milk_date DESC
        LIMIT 1;
END;
$$