show variables like "%timeout%";

show processlist;
show session status;

show status where `variable_name` = 'Threads_connected';

kill 1480389;
