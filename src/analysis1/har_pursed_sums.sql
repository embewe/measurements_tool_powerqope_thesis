SELECT
            uuid,
            experiment,   
 	    recursive,
	    dns_type,
            domain,
            sum(ssl_time) as ssl_time,
            sum(dns_time) as dns_time,
            sum(tcp_handshake) as tcp_time,
            pageload,
            sum(requestHeadersSize) as requestHeadersSize,
	    sum(responseBodySize) as responseBodySize,
            sum(responseHeadersSize) as responseHeadersSize,
	    sum(responseBodySize) as responseBodySize,
	    avg(a.rtt1::double precision + a.rtt2::double precision + a.rtt3::double precision + a.rtt4::double precision + a.rtt5::double precision) AS avg_rtt_to_resolver,
	    avg(a.rttd1::double precision + a.rttd2::double precision + a.rttd3::double precision + a.rttd4::double precision + a.rttd5::double precision) AS avg_rtt_to_domain
	    
        FROM (
        SELECT 
		uuid,
		experiment,
		recursive,
		dns_type,
		domain,  
		(jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'request')->>'url') as url,
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'serverIPAddress')) as serverIPAddress,
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'request')->>'httpVersion') as HTTP_Version,
		(jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'timings')->>'ssl')::float as SSL_time,
		(jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'timings')->>'dns')::float as DNS_time,
	        (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'timings')->>'connect')::float as TCP_handshake,
		(jsonb_extract_path(har, 'pages', '0', 'pageTimings')->>'onLoad')::float as pageload,
		(jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'request')->>'headersSize')::float as requestHeadersSize,
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'request')->>'bodySize'):: float as requestBodySize,
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'response')->>'headersSize')::float as responseHeadersSize,
                (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'response')->>'bodySize')::float as responseBodySize,
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
            har
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
	    a.responseBodySize
	    
     INTO har_pursed_sums

