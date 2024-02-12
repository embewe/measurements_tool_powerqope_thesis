DROP FUNCTION har_pursed(_tbl text);
CREATE OR REPLACE FUNCTION har_pursed(_tbl text)
    RETURNS TABLE (
	vantage_point text,
	experiment uuid,
        recursive text,
        dns_type text,
        domain text,
	cipher text,
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
	    vantage_point,
	    experiment,
	    recursive,
	    dns_type,
            domain,
	    cipher,
            avg(SSL_time) as SSL_time,
            avg(DNS_time) as DNS_time,
            avg(TCP_handshake) as TCP_handshake,
            avg(pageload) as pageload,
            avg(requestHeadersSize) as requestHeadersSize,
	    avg(requestBodySize) as responseBodySize,
            avg(responseHeadersSize) as responseHeadersSize,
	    avg(responseBodySize) as responseBodySize
        FROM (
        SELECT 
		vantage_point,
		experiment,
		recursive,
		dns_type,
	    	domain,  
	        cipher,
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
	    vantage_point,
            experiment,
            recursive,
            dns_type,
   	    domain,
     	    cipher,		
            har
        ORDER BY
            recursive ASC
        ) AS y WHERE y.pageload<>0 GROUP BY 
	    y.vantage_point,
            y.experiment,
	    y.recursive,
            y.dns_type,
	    y.domain, 
	    y.cipher;' , _tbl);
        END
    $f$
    LANGUAGE plpgsql;

\echo 'Function created successfully' 
\echo '======' 

