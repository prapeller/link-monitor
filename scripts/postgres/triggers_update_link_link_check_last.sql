DROP FUNCTION IF EXISTS update_link_link_check_last_id;
CREATE  FUNCTION update_link_link_check_last_id()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE link
    SET link_check_last_id = NEW.id,
        link_check_last_status = NEW.status,
        link_check_last_result_message = NEW.result_message
    WHERE id = NEW.link_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_link_link_check_last_id on link_check;
CREATE TRIGGER update_link_link_check_last_id
    BEFORE UPDATE
    ON
        link_check
    FOR EACH ROW
EXECUTE PROCEDURE update_link_link_check_last_id();
