CREATE OR REPLACE FUNCTION check_cows_changes() RETURNS TRIGGER AS
$$
BEGIN
    -- Check if cow_id, place_id, barn_id are being updated
    IF OLD IS NOT NULL AND NEW IS NOT NULL AND (
                OLD.cow_id <> NEW.cow_id OR
                OLD.place_id <> NEW.place_id OR
                OLD.barn_id <> NEW.barn_id
        ) THEN
        RAISE EXCEPTION 'Updating cow_id, place_id, barn_id, or milk_time is not allowed';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger for the cows table
CREATE OR REPLACE TRIGGER cows_changes_trigger
    BEFORE UPDATE
    ON cows
    FOR EACH ROW
EXECUTE FUNCTION check_cows_changes();

CREATE OR REPLACE FUNCTION check_milk_production_changes() RETURNS TRIGGER AS
$$
BEGIN
    -- Check if cow_id and milk_time are being updated
    IF OLD IS NOT NULL AND NEW IS NOT NULL AND (
                OLD.cow_id <> NEW.cow_id OR
                OLD.milk_date <> NEW.milk_date
        ) THEN
        RAISE EXCEPTION 'Updating cow_id or milk_time in f_milk_production is not allowed';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger for the f_milk_production table
CREATE OR REPLACE TRIGGER milk_production_changes_trigger
    BEFORE UPDATE
    ON f_milk_production
    FOR EACH ROW
EXECUTE FUNCTION check_milk_production_changes();

CREATE OR REPLACE FUNCTION check_diets_cows_changes() RETURNS TRIGGER AS
$$
BEGIN
    -- Check if cow_id, start_date, and end_date are being updated
    IF OLD IS NOT NULL AND NEW IS NOT NULL AND (
                OLD.cow_id <> NEW.cow_id OR
                OLD.start_date <> NEW.start_date OR
                OLD.end_date <> NEW.end_date
        ) THEN
        RAISE EXCEPTION 'Updating cow_id, start_date, or end_date in f_diets_cows is not allowed';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger for the f_diets_cows table
CREATE OR REPLACE TRIGGER diets_cows_changes_trigger
    BEFORE UPDATE
    ON f_diets_cows
    FOR EACH ROW
EXECUTE FUNCTION check_diets_cows_changes();

