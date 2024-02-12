SELECT a.uuid,
    a.experiment,
    a.vantage_point,
    a.domain,
    a.recursive,
    a.dns_type,
    avg(a.rtt1::double precision + a.rtt2::double precision + a.rtt3::double precision + a.rtt4::double precision + a.rtt5::double precision) AS avg_rtt
   INTO ping_table_filter
   FROM ( SELECT uuid,
            experiment,
            vantage_point,
            domain,
            recursive,
            dns_type,
            delays ->> 0 AS rtt1,
            delays ->> 1 AS rtt2,
            delays ->> 2 AS rtt3,
            delays ->> 2 AS rtt4,
            delays ->> 4 AS rtt5
           FROM har
          WHERE har <> 'null'::jsonb) a
  GROUP BY a.uuid, a.experiment, a.vantage_point, a.domain, a.recursive, a.dns_type;
