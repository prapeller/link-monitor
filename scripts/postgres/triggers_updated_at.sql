CREATE  FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_link on link;
CREATE TRIGGER update_link
    BEFORE UPDATE
    ON
        link
    FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();

DROP TRIGGER IF EXISTS update_link_check on link_check;
CREATE TRIGGER update_link_check
    BEFORE UPDATE
    ON
        link_check
    FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();

DROP TRIGGER IF EXISTS update_link_url_domain on link_url_domain;
CREATE TRIGGER update_link_url_domain
    BEFORE UPDATE
    ON
        link_url_domain
    FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();

DROP TRIGGER IF EXISTS update_page_url_domain on page_url_domain;
CREATE TRIGGER update_page_url_domain
    BEFORE UPDATE
    ON
        page_url_domain
    FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();

DROP TRIGGER IF EXISTS update_user on "user";
CREATE TRIGGER update_user
    BEFORE UPDATE
    ON
        "user"
    FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();