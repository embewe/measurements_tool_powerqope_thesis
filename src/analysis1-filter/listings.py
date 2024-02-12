
adguard_nofilter_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="adguard_nofilter" and dns_type=="dns"')['pageload'].dropna()
adguard_nofilter_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="adguard_nofilter" and dns_type=="dns"')['pageload'].dropna()
adguard_nofilter_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="adguard_nofilter" and dns_type=="dns"')['pageload'].dropna()
adguard_nofilter_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="adguard_nofilter" and dns_type=="dot"')['pageload'].dropna()
adguard_nofilter_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="adguard_nofilter" and dns_type=="dot"')['pageload'].dropna()
adguard_nofilter_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="adguard_nofilter" and dns_type=="dot"')['pageload'].dropna()
adguard_nofilter_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="adguard_nofilter" and dns_type=="doh"')['pageload'].dropna()
adguard_nofilter_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="adguard_nofilter" and dns_type=="doh"')['pageload'].dropna()
adguard_nofilter_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="adguard_nofilter" and dns_type=="doh"')['pageload'].dropna()

adguard_adblock_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="adguard_adblock" and dns_type=="dns"')['pageload'].dropna()
adguard_adblock_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="adguard_adblock" and dns_type=="dns"')['pageload'].dropna()
adguard_adblock_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="adguard_adblock" and dns_type=="dns"')['pageload'].dropna()
adguard_adblock_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="adguard_adblock" and dns_type=="dot"')['pageload'].dropna()
adguard_adblock_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="adguard_adblock" and dns_type=="dot"')['pageload'].dropna()
adguard_adblock_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="adguard_adblock" and dns_type=="dot"')['pageload'].dropna()
adguard_adblock_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="adguard_adblock" and dns_type=="doh"')['pageload'].dropna()
adguard_adblock_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="adguard_adblock" and dns_type=="doh"')['pageload'].dropna()
adguard_adblock_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="adguard_adblock" and dns_type=="doh"')['pageload'].dropna()

adguard_family_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="adguard_family" and dns_type=="dns"')['pageload'].dropna()
adguard_family_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="adguard_family" and dns_type=="dns"')['pageload'].dropna()
adguard_family_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="adguard_family" and dns_type=="dns"')['pageload'].dropna()
adguard_family_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="adguard_family" and dns_type=="dot"')['pageload'].dropna()
adguard_family_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="adguard_family" and dns_type=="dot"')['pageload'].dropna()
adguard_family_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="adguard_family" and dns_type=="dot"')['pageload'].dropna()
adguard_family_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="adguard_family" and dns_type=="doh"')['pageload'].dropna()
adguard_family_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="adguard_family" and dns_type=="doh"')['pageload'].dropna()
adguard_family_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="adguard_family" and dns_type=="doh"')['pageload'].dropna()



cleanbrowsing_adult_filter_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="cleanbrowsing_adult_filter" and dns_type=="dns"')['pageload'].dropna()
cleanbrowsing_adult_filter_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="cleanbrowsing_adult_filter" and dns_type=="dns"')['pageload'].dropna()
cleanbrowsing_adult_filter_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cleanbrowsing_adult_filter" and dns_type=="dns"')['pageload'].dropna()
cleanbrowsing_adult_filter_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="cleanbrowsing_adult_filter" and dns_type=="doh"')['pageload'].dropna()
cleanbrowsing_adult_filter_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="cleanbrowsing_adult_filter" and dns_type=="doh"')['pageload'].dropna()
cleanbrowsing_adult_filter_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cleanbrowsing_adult_filter" and dns_type=="doh"')['pageload'].dropna()
cleanbrowsing_adult_filter_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="cleanbrowsing_adult_filter" and dns_type=="dot"')['pageload'].dropna()
cleanbrowsing_adult_filter_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="cleanbrowsing_adult_filter" and dns_type=="dot"')['pageload'].dropna()
cleanbrowsing_adult_filter_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cleanbrowsing_adult_filter" and dns_type=="dot"')['pageload'].dropna()

cleanbrowsing_family_filter_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="cleanbrowsing_family_filter" and dns_type=="dns"')['pageload'].dropna()
cleanbrowsing_family_filter_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="cleanbrowsing_family_filter" and dns_type=="dns"')['pageload'].dropna()
cleanbrowsing_family_filter_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cleanbrowsing_family_filter" and dns_type=="dns"')['pageload'].dropna()
cleanbrowsing_family_filter_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="cleanbrowsing_family_filter" and dns_type=="doh"')['pageload'].dropna()
cleanbrowsing_family_filter_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="cleanbrowsing_family_filter" and dns_type=="doh"')['pageload'].dropna()
cleanbrowsing_family_filter_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cleanbrowsing_family_filter" and dns_type=="doh"')['pageload'].dropna()
cleanbrowsing_family_filter_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="cleanbrowsing_family_filter" and dns_type=="dot"')['pageload'].dropna()
cleanbrowsing_family_filter_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="cleanbrowsing_family_filter" and dns_type=="dot"')['pageload'].dropna()
cleanbrowsing_family_filter_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cleanbrowsing_family_filter" and dns_type=="dot"')['pageload'].dropna()

cleanbrowsing_security_filter_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="cleanbrowsing_security_filter" and dns_type=="dns"')['pageload'].dropna()
cleanbrowsing_security_filter_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="cleanbrowsing_security_filter" and dns_type=="dns"')['pageload'].dropna()
cleanbrowsing_security_filter_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cleanbrowsing_security_filter" and dns_type=="dns"')['pageload'].dropna()
cleanbrowsing_security_filter_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="cleanbrowsing_security_filter" and dns_type=="doh"')['pageload'].dropna()
cleanbrowsing_security_filter_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="cleanbrowsing_security_filter" and dns_type=="doh"')['pageload'].dropna()
cleanbrowsing_security_filter_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cleanbrowsing_security_filter" and dns_type=="doh"')['pageload'].dropna()
cleanbrowsing_security_filter_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="cleanbrowsing_security_filter" and dns_type=="dot"')['pageload'].dropna()
cleanbrowsing_security_filter_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="cleanbrowsing_security_filter" and dns_type=="dot"')['pageload'].dropna()
cleanbrowsing_security_filter_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cleanbrowsing_security_filter" and dns_type=="dot"')['pageload'].dropna()



cloudflare_nofilter_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="cloudflare_nofilter" and dns_type=="dns"')['pageload'].dropna()
cloudflare_nofilter_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="cloudflare_nofilter" and dns_type=="dns"')['pageload'].dropna()
cloudflare_nofilter_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cloudflare_nofilter" and dns_type=="dns"')['pageload'].dropna()
cloudflare_nofilter_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="cloudflare_nofilter" and dns_type=="doh"')['pageload'].dropna()
cloudflare_nofilter_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="cloudflare_nofilter" and dns_type=="doh"')['pageload'].dropna()
cloudflare_nofilter_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cloudflare_nofilter" and dns_type=="doh"')['pageload'].dropna()
cloudflare_nofilter_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="cloudflare_nofilter" and dns_type=="dot"')['pageload'].dropna()
cloudflare_nofilter_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="cloudflare_nofilter" and dns_type=="dot"')['pageload'].dropna()
cloudflare_nofilter_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cloudflare_nofilter" and dns_type=="dot"')['pageload'].dropna()

cloudflare_family_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="cloudflare_family" and dns_type=="dns"')['pageload'].dropna()
cloudflare_family_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="cloudflare_family" and dns_type=="dns"')['pageload'].dropna()
cloudflare_family_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cloudflare_family" and dns_type=="dns"')['pageload'].dropna()
cloudflare_family_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="cloudflare_family" and dns_type=="doh"')['pageload'].dropna()
cloudflare_family_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="cloudflare_family" and dns_type=="doh"')['pageload'].dropna()
cloudflare_family_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cloudflare_family" and dns_type=="doh"')['pageload'].dropna()
cloudflare_family_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="cloudflare_family" and dns_type=="dot"')['pageload'].dropna()
cloudflare_family_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="cloudflare_family" and dns_type=="dot"')['pageload'].dropna()
cloudflare_family_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cloudflare_family" and dns_type=="dot"')['pageload'].dropna()

cloudflare_security_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="cloudflare_security" and dns_type=="dns"')['pageload'].dropna()
cloudflare_security_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="cloudflare_security" and dns_type=="dns"')['pageload'].dropna()
cloudflare_security_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cloudflare_security" and dns_type=="dns"')['pageload'].dropna()
cloudflare_security_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="cloudflare_security" and dns_type=="doh"')['pageload'].dropna()
cloudflare_security_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="cloudflare_security" and dns_type=="doh"')['pageload'].dropna()
cloudflare_security_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cloudflare_security" and dns_type=="doh"')['pageload'].dropna()
cloudflare_security_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="cloudflare_security" and dns_type=="dot"')['pageload'].dropna()
cloudflare_security_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="cloudflare_security" and dns_type=="dot"')['pageload'].dropna()
cloudflare_security_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="cloudflare_security" and dns_type=="dot"')['pageload'].dropna()

quad9_nofilter_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="quad9_nofilter" and dns_type=="dns"')['pageload'].dropna()
quad9_nofilter_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="quad9_nofilter" and dns_type=="dns"')['pageload'].dropna()
quad9_nofilter_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="quad9_nofilter" and dns_type=="dns"')['pageload'].dropna()
quad9_nofilter_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="quad9_nofilter" and dns_type=="doh"')['pageload'].dropna()
quad9_nofilter_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="quad9_nofilter" and dns_type=="doh"')['pageload'].dropna()
quad9_nofilter_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="quad9_nofilter" and dns_type=="doh"')['pageload'].dropna()
quad9_nofilter_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="quad9_nofilter" and dns_type=="dot"')['pageload'].dropna()
quad9_nofilter_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="quad9_nofilter" and dns_type=="dot"')['pageload'].dropna()
quad9_nofilter_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="quad9_nofilter" and dns_type=="dot"')['pageload'].dropna()

quad9_security_wired_dns=plt_filter.query('vantage_point=="wired" and recursive=="quad9_security" and dns_type=="dns"')['pageload'].dropna()
quad9_security_eduroam_dns=plt_filter.query('vantage_point=="eduroam" and recursive=="quad9_security" and dns_type=="dns"')['pageload'].dropna()
quad9_security_vodacom_4g_dns=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="quad9_security" and dns_type=="dns"')['pageload'].dropna()
quad9_security_wired_doh=plt_filter.query('vantage_point=="wired" and recursive=="quad9_security" and dns_type=="doh"')['pageload'].dropna()
quad9_security_eduroam_doh=plt_filter.query('vantage_point=="eduroam" and recursive=="quad9_security" and dns_type=="doh"')['pageload'].dropna()
quad9_security_vodacom_4g_doh=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="quad9_security" and dns_type=="doh"')['pageload'].dropna()
quad9_security_wired_dot=plt_filter.query('vantage_point=="wired" and recursive=="quad9_security" and dns_type=="dot"')['pageload'].dropna()
quad9_security_eduroam_dot=plt_filter.query('vantage_point=="eduroam" and recursive=="quad9_security" and dns_type=="dot"')['pageload'].dropna()
quad9_security_vodacom_4g_dot=plt_filter.query('vantage_point=="vodacom_4g" and recursive=="quad9_security" and dns_type=="dot"')['pageload'].dropna()



Adguard_wired_A=['adguard_nofilter_wired_dns',
                'adguard_nofilter_wired_dot',
                'adguard_nofilter_wired_doh',
                'adguard_adblock_wired_dns',
                'adguard_adblock_wired_dot',
                'adguard_adblock_wired_doh',
                'adguard_family_wired_dns',
                'adguard_family_wired_dot',
                'adguard_family_wired_doh'
            ]

Adguard_wired_B=['adguard_nofilter_wired_dns',
                'adguard_nofilter_wired_dot',
                'adguard_nofilter_wired_doh',
                'adguard_adblock_wired_dns',
                'adguard_adblock_wired_dot',
                'adguard_adblock_wired_doh',
                'adguard_family_wired_dns',
                'adguard_family_wired_dot',
                'adguard_family_wired_doh'
            ]

Adguard_Eduroam_A=[adguard_nofilter_eduroam_dns
                    adguard_nofilter_eduroam_dot
                    adguard_nofilter_eduroam_doh
                    adguard_adblock_eduroam_dns
                    adguard_adblock_eduroam_dot
                    adguard_adblock_eduroam_doh
                    adguard_family_eduroam_dns
                    adguard_family_eduroam_dot
                    adguard_family_eduroam_doh
                ]

Adguard_Eduroam_B=[adguard_nofilter_eduroam_dns
                    adguard_nofilter_eduroam_dot
                    adguard_nofilter_eduroam_doh
                    adguard_adblock_eduroam_dns
                    adguard_adblock_eduroam_dot
                    adguard_adblock_eduroam_doh
                    adguard_family_eduroam_dns
                    adguard_family_eduroam_dot
                    adguard_family_eduroam_doh
                ]


Adguard_4G_A=[adguard_nofilter_vodacom_4g_dns
            adguard_nofilter_vodacom_4g_dot
            adguard_nofilter_vodacom_4g_doh
            adguard_adblock_vodacom_4g_dns
            adguard_adblock_vodacom_4g_dot
            adguard_adblock_vodacom_4g_doh
            adguard_family_vodacom_4g_dns
            adguard_family_vodacom_4g_dot
            adguard_family_vodacom_4g_doh    
        ]

Adguard_4G_B=[adguard_nofilter_vodacom_4g_dns
            adguard_nofilter_vodacom_4g_dot
            adguard_nofilter_vodacom_4g_doh
            adguard_adblock_vodacom_4g_dns
            adguard_adblock_vodacom_4g_dot
            adguard_adblock_vodacom_4g_doh
            adguard_family_vodacom_4g_dns
            adguard_family_vodacom_4g_dot
            adguard_family_vodacom_4g_doh    
        ]

##Cleanbrowsing
CleanB_Wired_A=[cleanbrowsing_adult_filter_wired_dns,
                cleanbrowsing_adult_filter_wired_doh,
                cleanbrowsing_adult_filter_wired_dot,
                cleanbrowsing_family_filter_wired_dns,
                cleanbrowsing_family_filter_wired_doh,
                cleanbrowsing_family_filter_wired_dot,
                cleanbrowsing_security_filter_wired_dns,
                cleanbrowsing_security_filter_wired_doh,
                cleanbrowsing_security_filter_wired_dot         
            ]


CleanB_Eduroam_A=[cleanbrowsing_adult_filter_eduroam_dns,
                cleanbrowsing_adult_filter_eduroam_doh,
                cleanbrowsing_adult_filter_eduroam_dot,
                cleanbrowsing_family_filter_eduroam_dns,
                cleanbrowsing_family_filter_eduroam_doh,
                cleanbrowsing_family_filter_eduroam_dot,
                cleanbrowsing_security_filter_eduroam_dns,
                cleanbrowsing_security_filter_eduroam_doh,
                cleanbrowsing_security_filter_eduroam_dot
            ]


CleanB_4G_A=[cleanbrowsing_adult_filter_vodacom_4g_dns,
            cleanbrowsing_adult_filter_vodacom_4g_doh,
            cleanbrowsing_adult_filter_vodacom_4g_dot,
            cleanbrowsing_family_filter_vodacom_4g_dns,
            cleanbrowsing_family_filter_vodacom_4g_doh,
            cleanbrowsing_family_filter_vodacom_4g_dot,
            cleanbrowsing_security_filter_vodacom_4g_dns,
            cleanbrowsing_security_filter_vodacom_4g_doh,
            cleanbrowsing_security_filter_vodacom_4g_dot
        ]

CF_Wired_A=[cloudflare_nofilter_wired_dns,
            cloudflare_nofilter_wired_doh,
            cloudflare_nofilter_wired_dot,
            cloudflare_family_wired_dns,
            cloudflare_family_wired_doh,
            cloudflare_family_wired_dot,
            cloudflare_security_wired_dns,
            cloudflare_security_wired_doh,
            cloudflare_security_wired_dot
        ]

CF_Eduroam_A=[cloudflare_nofilter_eduroam_dns,
            cloudflare_nofilter_eduroam_doh,
            cloudflare_nofilter_eduroam_dot,
            cloudflare_family_eduroam_dns,
            cloudflare_family_eduroam_doh,
            cloudflare_family_eduroam_dot,
            cloudflare_security_eduroam_dns,
            cloudflare_security_eduroam_doh,
            cloudflare_security_eduroam_dot
        ]

CF_4G_A=[cloudflare_nofilter_vodacom_4g_dns,
        cloudflare_nofilter_vodacom_4g_doh,
        cloudflare_nofilter_vodacom_4g_dot,
        cloudflare_family_vodacom_4g_dns,
        cloudflare_family_vodacom_4g_doh,
        cloudflare_family_vodacom_4g_dot,
        cloudflare_security_vodacom_4g_dns,
        cloudflare_security_vodacom_4g_doh,
        cloudflare_security_vodacom_4g_dot
    ]



Q9_Wired_A=[quad9_nofilter_wired_dns,
            quad9_nofilter_wired_doh,
            quad9_nofilter_wired_dot,
            quad9_security_wired_dns,
            quad9_security_wired_doh,
            quad9_security_wired_dot
        ]

Q9_Eduroam_A=[quad9_nofilter_eduroam_dns,
            quad9_nofilter_eduroam_doh,
            quad9_nofilter_eduroam_dot,
            quad9_security_eduroam_dns,
            quad9_security_eduroam_doh,
            quad9_security_eduroam_dot
        ]

Q9_4G_A=[quad9_nofilter_vodacom_4g_dns,
        quad9_nofilter_vodacom_4g_doh,
        quad9_nofilter_vodacom_4g_dot,
        quad9_security_vodacom_4g_dns,
        quad9_security_vodacom_4g_doh,
        quad9_security_vodacom_4g_dot
    ]





'102.5.23.39','168.253.229.13','197.210.8.132','197.211.118.115','197.239.6.118','41.13.220.74','41.174.3.15','41.175.171.25','41.204.127.136'









select 
		har_uuid,
		experiment,
		vantage_point,
		insertion_time,
		domain,
		recursive,
		dns_type,
		response_size,
		response_time,
		error
INTO mobile4G_to_filter_dns
FROM dns

WHERE vantage_point IN ('102.5.23.39','168.253.229.13','197.210.8.132','197.211.118.115','197.239.6.118','41.13.220.74','41.174.3.15','41.175.171.25','41.204.127.136')
		

select 
		uuid,
		experiment,
		vantage_point,
		insertion_time,
		domain,
		recursive,
		dns_type,
		har,
		error,
		delays
INTO mobile4G_to_filter_dns
FROM har

WHERE network_type='4G'















