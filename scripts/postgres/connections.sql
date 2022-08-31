-- kill all connections to database
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE
  -- don't kill this connection!
    pid <> pg_backend_pid()
  -- don't kill the connections to other databases
  AND datname = 'reportpostgres_db';

-- check number of connections to database
SELECT sum(numbackends) FROM pg_stat_database;

-- check number of connections to database
SELECT * from pg_stat_activity;

-- set timeout for idle transactions
alter system set idle_in_transaction_session_timeout = 0;
alter system set idle_session_timeout = 0;
SET SESSION idle_in_transaction_session_timeout='5min';
SET SESSION idle_in_transaction_session_timeout=0;
SET SESSION idle_session_timeout='5min';
SET SESSION idle_session_timeout=0;
show idle_in_transaction_session_timeout;
show idle_session_timeout;