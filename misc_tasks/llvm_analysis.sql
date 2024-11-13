EXPLAIN ANALYZE
SELECT to_jsonb(r) FROM
(SELECT 
  (select recovery from pg_gather) AS clsr,
  (SELECT to_jsonb(ROW(count(*),COUNT(*) FILTER (WHERE last_vac IS NULL), COUNT(*) FILTER (WHERE b.table_oid IS NULL AND r.n_live_tup != 0 ),COUNT(*) FILTER (WHERE last_anlyze IS NULL))) 
  FROM pg_get_rel r JOIN pg_get_class c ON r.relid = c.reloid AND c.relkind NOT IN ('t','p')
LEFT JOIN pg_tab_bloat b ON c.reloid = b.table_oid) AS tabs,
  (SELECT to_jsonb(ROW(COUNT(*),COUNT(*) FILTER (WHERE CONN < interval '15 minutes' ) )) FROM 
    (WITH g AS (SELECT MAX(state_change) as ts FROM pg_get_activity)
    SELECT pid,g.ts - backend_start CONN
    FROM pg_get_activity
    LEFT JOIN g ON true
    WHERE EXISTS (SELECT pid FROM pg_pid_wait WHERE pid=pg_get_activity.pid)
    AND backend_type='client backend') cn) AS cn,
  (SELECT to_jsonb(ROW(count(*) FILTER (WHERE relkind='p'), max(reloid))) from pg_get_class) as clas,
  (SELECT to_jsonb(ROW(count(*) FILTER (WHERE state='active' AND state IS NOT NULL), 
  count(*) FILTER (WHERE state='idle in transaction'), count(*) FILTER (WHERE state='idle'),
  count(*) FILTER (WHERE state IS NULL), count(*) FILTER (WHERE leader_pid IS NOT NULL) ,
  count(*),   count(distinct backend_type)))
  FROM pg_get_activity) as sess,
  (WITH curdb AS (SELECT 
  CASE WHEN (SELECT COUNT(*) FROM pg_srvr) > 0 
    THEN (SELECT trim(both '\"' from substring(connstr from '\"\w*\"')) "curdb" FROM pg_srvr WHERE connstr like '%to database%') ELSE (SELECT 'template1' "curdb")
  END),
  cts AS (SELECT COALESCE((SELECT COALESCE(collect_ts,(SELECT max(state_change) FROM pg_get_activity)) FROM pg_gather),current_timestamp) AS c_ts)
  SELECT to_jsonb(ROW(curdb,COALESCE(pg_get_db.stats_reset,pg_get_wal.stats_reset),c_ts,days))
  FROM  curdb LEFT JOIN pg_get_db ON pg_get_db.datname=curdb.curdb
  LEFT JOIN pg_get_wal ON true
  LEFT JOIN LATERAL (SELECT GREATEST((EXTRACT(epoch FROM(c_ts- COALESCE(pg_get_db.stats_reset,pg_get_wal.stats_reset)))/86400)::bigint,1) as days FROM cts) AS lat1 ON TRUE
  LEFT JOIN cts ON true) as dbts,
  (WITH maxmxid AS (SELECT max(mxidage) FROM pg_get_db),
  topdbmx AS (SELECT array_agg(datname),maxmxid.max FROM pg_get_db JOIN maxmxid ON pg_get_db.mxidage=maxmxid.max AND pg_get_db.mxidage > 1000 GROUP BY 2)
  SELECT to_jsonb(ROW(array_agg,max)) FROM topdbmx) AS mxiddbs,
  (SELECT json_agg(pg_get_ns) FROM  pg_get_ns) AS ns,
  (SELECT json_agg(pg_get_tablespace) FROM pg_get_tablespace) AS tbsp,
  (SELECT to_jsonb((extract (EPOCH FROM (collect_ts - last_archived_time)), pg_wal_lsn_diff( current_wal,
  (coalesce(nullif(CASE WHEN length(last_archived_wal) < 24 THEN '' ELSE ltrim(substring(last_archived_wal, 9, 8), '0') END, ''), '0') || '/' || substring(last_archived_wal, 23, 2) || '000001'        ) :: pg_lsn )
  , last_archived_wal, last_archived_time::text || ' (' || CASE WHEN EXTRACT(EPOCH FROM(collect_ts - last_archived_time)) < 0 THEN 'Right Now'::text ELSE (collect_ts - last_archived_time)::text END  || ')'))
  FROM  pg_gather,  pg_archiver_stat) AS arcfail,
  (SELECT to_jsonb(ROW(max(setting) FILTER (WHERE name = 'archive_library'), max(setting) FILTER (WHERE name = 'cluster_name'),count(*) FILTER (WHERE source = 'command line'))) FROM pg_get_confs) AS params,
  (WITH g AS (SELECT collect_ts,pg_start_ts,reload_ts,to_timestamp ( systemid >> 32 ) init_ts from pg_gather),
    r AS (SELECT LEAST(min(last_vac),min(last_anlyze)) known_ts FROM pg_get_rel)
  SELECT CASE WHEN (g.init_ts IS NULL OR g.reload_ts - g.init_ts > '80 minutes'::interval) AND ( r.known_ts > g.reload_ts OR r.known_ts IS NULL) AND g.collect_ts - g.reload_ts < '10 days'::interval 
  THEN g.reload_ts END crash_ts FROM g,r) crash,
  (WITH blockers AS (select array_agg(victim_pid) OVER () victim,blocking_pids blocker from pg_get_pidblock),
   ublokers as (SELECT unnest(blocker) AS blkr FROM blockers)
   SELECT json_agg(blkr) FROM ublokers
   WHERE NOT EXISTS (SELECT 1 FROM blockers WHERE ublokers.blkr = ANY(victim))) blkrs,
  (select json_agg((victim_pid,blocking_pids)) from pg_get_pidblock) victims,
  (SELECT  to_jsonb(( EXTRACT(epoch FROM (end_ts - collect_ts)),  pg_wal_lsn_diff(end_lsn, current_wal) * 60 * 60 / EXTRACT( epoch FROM (end_ts - collect_ts) ),
  wal_bytes/(extract (EPOCH FROM  (collect_ts - stats_reset))/3600)))
  FROM pg_gather JOIN pg_gather_end ON true
   LEFT JOIN pg_get_wal ON true) sumry,
  (SELECT json_agg((relname,maint_work_mem_gb)) FROM (SELECT relname,n_live_tup*0.2*6 maint_work_mem_gb 
   FROM pg_get_rel JOIN pg_get_class ON n_live_tup > 894784853 AND pg_get_rel.relid = pg_get_class.reloid 
   ORDER BY 2 DESC LIMIT 3) AS wmemuse) wmemuse,
   (WITH w AS (SELECT pid,count(*) cnt, max(itr) itr_max,min(itr) itr_min FROM pg_pid_wait group by 1),
   g AS (SELECT max(itr_max) gmax_itr FROM w)
  SELECT to_jsonb(ROW(SUM(((itr_max - itr_min)::float/gmax_itr)*2000 - cnt),max(gmax_itr),count(pid))) FROM w,g
   WHERE ((itr_max - itr_min)::float/gmax_itr)*2000 - cnt > 0) netdlay,
   (SELECT to_jsonb(ROW(count(*) FILTER (WHERE indisvalid=false)
   ,count(*) FILTER (WHERE numscans=0 AND tst.toastid IS NULL) --Unused Indexes of user tables
   ,count(*) FILTER (WHERE numscans=0 AND tst.toastid > 16384) --Unused TOAST index of user tables
   ,count(*) FILTER (WHERE tst.toastid IS NULL) --TOTAL User/Regular indexes
   ,count(*) FILTER (WHERE tst.toastid > 16384) --TOTAL Toast Indexes
   ,sum(size) FILTER (WHERE numscans=0)))
    FROM pg_get_index i
    JOIN pg_get_class ct ON i.indrelid = ct.reloid
    LEFT JOIN pg_get_toast tst ON ct.reloid = tst.toastid) induse,
   (SELECT to_jsonb(ROW(sum(tab_ind_size) FILTER (WHERE relid < 16384),count(*))) FROM pg_get_rel) meta
) r;