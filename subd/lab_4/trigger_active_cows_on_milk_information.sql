-- Create a function that calculates the percentage drop in average milk yield for a cow between the previous month and the current month
CREATE OR REPLACE FUNCTION check_milk_yield_drop() RETURNS TRIGGER AS
$$
DECLARE
    current_month              DATE;
    first_day_of_current_month DATE;
    first_day_of_prev_month    DATE;
    prev_month_start           DATE;
    prev_month_end             DATE;
    prev_month_avg             NUMERIC;
    current_month_avg          NUMERIC;
BEGIN
    -- Calculate the current month and the first day of the current month
    current_month := DATE_TRUNC('month', NOW()::DATE);
    first_day_of_current_month := current_month;

    -- Calculate the first day of the previous month
    first_day_of_prev_month := DATE_TRUNC('month', NOW()::DATE) - INTERVAL '1 month';

    -- Calculate the start and end dates of the previous month
    prev_month_start := first_day_of_prev_month;
    prev_month_end := first_day_of_current_month - INTERVAL '1 day';

    -- Calculate the average milk yield per day in the previous month
    SELECT AVG(milk_per_day_liters)
    INTO prev_month_avg
    FROM farm.farm_schema.f_milk_production
    WHERE cow_id = NEW.cow_id
      AND milk_date >= prev_month_start
      AND milk_date <= prev_month_end
    GROUP BY cow_id, DATE_TRUNC('month', milk_date);

    -- Calculate the average milk yield per day in the current month
    SELECT AVG(milk_per_day_liters)
    INTO current_month_avg
    FROM farm.farm_schema.f_milk_production
    WHERE cow_id = NEW.cow_id
      AND milk_date >= first_day_of_current_month
    GROUP BY cow_id, DATE_TRUNC('month', milk_date);

    -- Calculate the percentage drop in average milk yield
    IF prev_month_avg IS NOT NULL AND current_month_avg IS NOT NULL THEN
        IF prev_month_avg > 0 AND current_month_avg > 0 THEN
            IF ((prev_month_avg - current_month_avg) / prev_month_avg) >= 0.3 THEN
                -- Mark the cow for culling
                UPDATE farm.farm_schema.cows
                SET is_active = False
                WHERE cow_id = NEW.cow_id;
            END IF;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger that fires after INSERT or UPDATE on milk_production
CREATE TRIGGER check_milk_yield_trigger
    AFTER INSERT OR UPDATE
    ON farm.farm_schema.f_milk_production
    FOR EACH ROW
EXECUTE FUNCTION check_milk_yield_drop();
