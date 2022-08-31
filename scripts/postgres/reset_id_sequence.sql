-- Login to psql and run the following

-- What is the result?
SELECT MAX(id) FROM link_check;

-- Then run...
-- This should be higher than the last result.
SELECT nextval('link_check_id_seq');

-- If it's not higher... run this set the sequence last to your highest id.
-- (wise to run a quick pg_dump first...)

BEGIN;
-- protect against concurrent inserts while you update the counter
LOCK TABLE link_check IN EXCLUSIVE MODE;
-- Update the sequence
SELECT setval('link_check_id_seq', COALESCE((SELECT MAX(id)+1 FROM link_check), 1), false);
COMMIT;