select count(link.id)
from link;
select count(link_check.id)
from link_check;

-- link_id - link_check_id
select link.id       as link_id,
       link_check.id as link_check_id
from link
         join link_check on link.id = link_check.link_id
order by link_check_id, link_id;

-- link_id - link_check_last_id
select linkchecklasts.link_id, max(linkchecklasts.link_check_id) as linkcheck_last_id
from (select link.id       as link_id,
             link_check.id as link_check_id
      from link
               join link_check on link.id = link_check.link_id
      order by link_check_id, link_id) as linkchecklasts
group by linkchecklasts.link_id
order by linkchecklasts.link_id;

-- user_id, link_id, link_check_last_id, status
select l2.user_id, l.link_id, l.linkcheck_last_id, lc.status
from (select linkchecklasts.link_id, max(linkchecklasts.link_check_id) as linkcheck_last_id
      from (select link.id       as link_id,
                   link_check.id as link_check_id
            from link
                     join link_check on link.id = link_check.link_id
            order by link_check_id, link_id) as linkchecklasts
      group by linkchecklasts.link_id
      order by linkchecklasts.link_id) l
         join link_check as lc on l.linkcheck_last_id = lc.id
         join link l2 on lc.link_id = l2.id;

--count green lcl on user
select count(l.link_id)
from (select linkchecklasts.link_id, max(linkchecklasts.link_check_id) as linkcheck_last_id
      from (select link.id       as link_id,
                   link_check.id as link_check_id
            from link
                     join link_check on link.id = link_check.link_id
            order by link_check_id, link_id) as linkchecklasts
      group by linkchecklasts.link_id
      order by linkchecklasts.link_id) l
         join link_check as lc on l.linkcheck_last_id = lc.id
         join link l2 on lc.link_id = l2.id
where status = 'green'
  and user_id = 1;

-- count links that have changed status from red to green from 1st Jan2022 to now
select count(distinct l_lcl2.l_id)
from (select l_lcl.user_id,
             l_lcl.link_id  as l_id,
             l_lcl.lcl_id,
             l_lcl.lcl_status,
             lc3.id         as lc_id,
             lc3.status     as lc_status,
             lc3.created_at as lc_date
      from (select l2.user_id, l2.id as link_id, lcl.linkcheck_last_id as lcl_id, lc.status as lcl_status
            from (select linkchecks.link_id,
                         max(linkchecks.link_check_id) as linkcheck_last_id
                  from (select link.id       as link_id,
                               link_check.id as link_check_id
                        from link
                                 join link_check on link.id = link_check.link_id
                        order by link_id) as linkchecks
                  group by linkchecks.link_id
                  order by linkchecks.link_id) lcl
                     join link_check as lc on lcl.linkcheck_last_id = lc.id
                     join link l2 on lc.link_id = l2.id) as l_lcl
               join link_check lc3 on l_lcl.link_id = lc3.link_id
      where user_id = 1
        and lcl_status = 'green'
        and l_lcl.lcl_status != lc3.status
        and lc3.created_at >= date('2022-01-01') - interval '1 DAY'
        and lc3.created_at <= date(now()) + interval '1 DAY') as l_lcl2;

-- test check 100
select link_id, status, result_message
from link_check
where created_at > timestamp '2022-08-28 18:52:00'
--   and status = 'red' and result_message like '%playwright%'
  and link_id in
      (
2882,
14646,
15283,
31356,
2685,
2775,
15961,
2969,
2723,
30741
          )
