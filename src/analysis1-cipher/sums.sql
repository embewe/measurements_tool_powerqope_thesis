\pset border 2
\pset footer 'off' 

DROP FUNCTION har_pursed(_tbl text);
CREATE FUNCTION har_pursed(_tbl text)
    RETURNS TABLE (
        network_type text,
        recursive text,
        dns_type text,
        domain text,
        SSL_time double precision,
        DNS_time double precision,
        TCP_handshake double precision,
        pageload double precision,
        requestHeadersSize double precision,
        requestBodySize double precision,
	responseHeadersSize double precision,
	responseBodySize double precision
	
    )
    AS $f$
    BEGIN
        RETURN QUERY EXECUTE format('SELECT
	    network_type,	   
 	    recursive,
	    dns_type,
            domain,
            sum(SSL_time) as SSL_time,
            sum(DNS_time) as DNS_time,
            sum(TCP_handshake) as TCP_handshake,
            sum(pageload) as pageload,
            sum(requestHeadersSize) as requestHeadersSize,
	    sum(requestBodySize) as responseBodySize,
            sum(responseHeadersSize) as responseHeadersSize,
	    sum(responseBodySize) as responseBodySize
        FROM (
        SELECT 
		network_type,
		dns_type,
		recursive,
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
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, ''entries'')), ''response'')->>''bodySize'')::float as responseBodySize
         
        FROM
            %s
        GROUP BY
            network_type,
	    recursive,
            dns_type,
	    domain,
            har
        ORDER BY
            network_type ASC
        ) AS y GROUP BY y.network_type,
	    y.recursive,
            y.dns_type,
	    y.domain;' , _tbl);
        END
    $f$
    LANGUAGE plpgsql;

\echo 'Loss 0%' 
\echo '======' 
SELECT * FROM har_pursed('har');
