-- Create a function to check for existing records for all dates before today
CREATE OR REPLACE FUNCTION check_daily_milk_record() RETURNS TRIGGER AS
$$
DECLARE
    start_date date;
    end_date   date;
BEGIN
    -- Get the start date (minimum date in the data_table)
    SELECT MIN(milk_date) INTO start_date FROM farm.farm_schema.f_milk_production WHERE cow_id = NEW.cow_id;

    -- Get the current date (date being inserted or updated)
    end_date := NEW.milk_date;

    -- Loop through dates from start_date to current_date
    WHILE start_date <= end_date
        LOOP
            -- Check if the date exists in the data_table
            IF NOT EXISTS (SELECT 1
                           FROM farm.farm_schema.f_milk_production
                           WHERE milk_date = start_date AND cow_id = NEW.cow_id) THEN
                RAISE NOTICE 'Data is missing for date: %', start_date;
            END IF;
            -- Move to the next date
            start_date := start_date + INTERVAL '1 day';
        END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to call the function before INSERT
CREATE OR REPLACE TRIGGER monitor_daily_milk_record
    BEFORE INSERT
    ON farm.farm_schema.f_milk_production
    FOR EACH ROW
EXECUTE FUNCTION check_daily_milk_record();
