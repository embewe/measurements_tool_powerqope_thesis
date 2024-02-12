\pset border 2
\pset footer 'off' 

DROP FUNCTION har_pursed(_tbl text);
CREATE FUNCTION har_pursed(_tbl text)
    RETURNS TABLE (
    	uuid uuid,
    	experiment uuid,
        recursive text,
        dns_type text,
        domain text,
        ssl_time double precision,
        dns_time double precision,
        tcp_handshake double precision,
        pageload double precision,
        requestHeadersSize double precision,
        requestBodySize double precision,
	responseHeadersSize double precision,
	responseBodySize double precision, 
	avg_rtt_to_resolver double precision,
	avg_rtt_to_domain double precision
    )
    AS $f$
    BEGIN
        RETURN QUERY EXECUTE format('SELECT
            uuid,
            experiment,   
 	    recursive,
	    dns_type,
            domain,
            ssl_time,
            dns_time,
            tcp_handshake,
            pageload,
            requestHeadersSize,
	    responseBodySize,
            responseHeadersSize,
	    responseBodySize,
	    avg(a.rtt1::double precision + a.rtt2::double precision + a.rtt3::double precision + a.rtt4::double precision + a.rtt5::double precision) AS avg_rtt_to_resolver,
	    avg(a.rttd1::double precision + a.rttd2::double precision + a.rttd3::double precision + a.rttd4::double precision + a.rttd5::double precision) AS avg_rtt_to_domain
	    
        FROM (
        SELECT 
		uuid,
		experiment,
		recursive,
		dns_type,
		domain,  
		(jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''request'')->>''url'') as url,
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''serverIPAddress'')) as serverIPAddress,
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''request'')->>''httpVersion'') as HTTP_Version,
		(jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''timings'')->>''ssl'')::float as SSL_time,
		(jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''timings'')->>''dns'')::float as DNS_time,
	        (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''timings'')->>''connect'')::float as TCP_handshake,
		(jsonb_extract_path(har, ''pages'', ''0'', ''pageTimings'')->>''onLoad'')::float as pageload,
		(jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''request'')->>''headersSize'')::float as requestHeadersSize,
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''request'')->>''bodySize''):: float as requestBodySize,
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''response'')->>''headersSize'')::float as responseHeadersSize,
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''response'')->>''bodySize'')::float as responseBodySize,
                delays ->> 0 AS rtt1,
                delays ->> 1 AS rtt2,
                delays ->> 2 AS rtt3,
                delays ->> 2 AS rtt4,
                delays ->> 4 AS rtt5,
                webdelays ->> 0 AS rttd1,
                webdelays ->> 1 AS rttd2,
                webdelays ->> 2 AS rttd3,
                webdelays ->> 2 AS rttd4,
                webdelays ->> 4 AS rttd5
                
         
        FROM
            %s
        ORDER BY
            recursive ASC
        ) AS a GROUP BY a.uuid,
            a.experiment,
	    a.recursive,
            a.dns_type,
	    a.domain,
	    a.ssl_time,
            a.dns_time,
            a.tcp_handshake,
            a.pageload,
            a.requestHeadersSize,
	    a.responseBodySize,
            a.responseHeadersSize,
	    a.responseBodySize;' , _tbl);
        END
    $f$
    LANGUAGE plpgsql;

\echo 'Loss 0%' 
\echo '======' 
SELECT * FROM har_pursed('har');
