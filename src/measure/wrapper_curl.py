#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import enum
import itertools
import json
import logging.config
import random
import re
import subprocess
import time
import uuid

from database import DNSDatabase
from ping_util import ping_resolver
from response_size import get_dns_sizes, get_doh_sizes
from dns_timings import measure_dns
from TCP_timings import tcp_timings



class Resolvers(enum.Enum):
    default = (None, None)
    cloudflare_standard = ('1.1.1.1', 'https://cloudflare-dns.com/dns-query')
    cloudflare_security = ('1.1.1.2', ' https://security.cloudflare-dns.com/dns-query')
    cloudflare_family = ('1.1.1.3', 'https://family.cloudflare-dns.com/dns-query')
    google = ('8.8.8.8', 'https://dns.google/dns-query')
    quad9_standard = ('9.9.9.10', 'https://dns10.quad9.net/dns-query')
    quad9_security = ('9.9.9.9', ' https://dns9.quad9.net/dns-query')
    quad9_security_edns = ('9.9.9.11', ' https://dns11.quad9.net/dns-query')
    cleanbrowsing_family=('185.228.168.9','https://doh.cleanbrowsing.org/doh/family-filter')
    cleanbrowsing_adult=('185.228.168.10','https://doh.cleanbrowsing.org/doh/adult-filter')
    cleanbrowsing_standard=('185.228.168.168','https://doh.cleanbrowsing.org/doh/security-filter')
    securedns_standard=('146.185.167.43','https://doh.securedns.eu/dns-query')
    securedns_adblock=('146.185.167.43','https://ads-doh.securedns.eu/dns-query')
    adguard_standard=('176.103.130.136','https://dns-unfiltered.adguard.com/dns-query')
    adguard_adblock=('176.103.130.131','https://dns.adguard.com/dns-query')
    adguard_family=('176.103.130.132','https://dns-family.adguard.com/dns-query')
    opendns_standard=('208.67.222.222','https://doh.opendns.com/dns-query')
    opendns_family=('208.67.222.123',' https://doh.familyshield.opendns.com/dns-query')
    libredns_standard=('116.202.176.26','https://doh.libredns.gr/dns-query')
    libredns_adblock=('116.202.176.26','https://doh.libredns.gr/ads')
    
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('database_config_file')
    parser.add_argument('website_list')
    parser.add_argument('log_config_file')
    parser.add_argument('experiment')
    parser.add_argument('start_index', type=int)
    parser.add_argument('stop_index', type=int)
    args = parser.parse_args()

    # Set up a logger
    logging.config.fileConfig(args.log_config_file)
    logging.basicConfig(filename='measurement.log',level=logging.DEBUG)
    log = logging.getLogger('wrapper')

    # Load the list of websites to measure from disk
    websites = load_websites(args.website_list)
    websites_subset = websites[args.start_index:args.stop_index]

    # Connect to the database for storing HARs
    db = DNSDatabase.init_from_config_file(args.database_config_file)

    # Run the measurements
    log.info("Starting new run through ALL configurations")
    start_time = time.time()
    start_ifconfig = "start_ifconfig_{0}.txt".format(args.experiment)
    save_ifconfig(start_ifconfig)

    run(log, db, args.experiment, websites_subset)

    end_time = time.time()
    end_ifconfig = "end_ifconfig_{0}.txt".format(args.experiment)
    save_ifconfig(end_ifconfig)
    log.info("elapsed time: %f seconds", end_time - start_time)


def save_ifconfig(filename):
    ifconfig = subprocess.check_output(["/sbin/ifconfig"])
    ifconfig = ifconfig.decode("utf-8")
    with open(filename, "w") as f:
        f.write(ifconfig)


def get_default_nameservers():
    # Parse the name servers from /etc/resolv.conf
    nameservers = []
    with open("/etc/resolv.conf") as f:
        for line in f:
            if line.startswith("nameserver "):
                _, nameserver = line.split(" ", 1)
                nameserver = nameserver[:-1]
                nameservers.append(nameserver)
    return nameservers[0]


def run(log, db, experiment, websites):
    dns_options = ['dns', 'doh', 'dot']
    recursive_options = ['default', 'cloudflare_standard', 'cloudflare_security', 'cloudflare_family',
                        'quad9_standard','quad9_security','quad9_security_edns',
                        'cleanbrowsing_adult',
                        'cleanbrowsing_standard',
                        'cleanbrowsing_family',
                        'securedns_standard','securedns_adblock',
                        'adguard_standard','adguard_adblock','adguard_family',
                        'opendns_standard','opendns_family','libredns_standard',
                        'libredns_adblock'
                       ]
    
    ciphers=['security.ssl3.TLS_AES_128_GCM_SHA256',
            'security.ssl3.TLS_AES_256_GCM_SHA384',
            'security.ssl3.TLS_CHACHA20_POLY1305_SHA256',
            'security.ssl3.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256',
            'security.ssl3.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256',
            'security.ssl3.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384',
            'security.ssl3.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384',
            'security.ssl3.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256',
            'security.ssl3.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256',
            'security.ssl3.TLS_DHE_RSA_WITH_AES_256_GCM_SHA384',
            'security.ssl3.TLS_DHE_RSA_WITH_AES_128_GCM_SHA256',
            'security.ssl3.TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256',
            'security.ssl3.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256',
            'security.ssl3.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384',
            'security.ssl3.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384',
            'security.ssl3.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256',
            'security.ssl3.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256',
            'security.ssl3.TLS_DHE_RSA_WITH_AES_128_GCM_SHA256',
            'security.ssl3.TLS_DHE_RSA_WITH_AES_256_GCM_SHA384',
            'security.ssl3.TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256',
            'security.ssl3.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256',
            'security.ssl3.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256',
            'security.ssl3.TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA',
            'security.ssl3.TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA',
            'security.ssl3.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384',
            'security.ssl3.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384',
            'security.ssl3.TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA',
            'security.ssl3.TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA',
            'security.ssl3.TLS_DHE_RSA_WITH_AES_128_CBC_SHA256',
            'security.ssl3.TLS_DHE_RSA_WITH_AES_256_CBC_SHA256',
            'security.ssl3.TLS_RSA_WITH_AES_128_GCM_SHA256',
            'security.ssl3.TLS_RSA_WITH_AES_256_GCM_SHA384',
            'security.ssl3.TLS_RSA_WITH_AES_128_CBC_SHA256',
            'security.ssl3.TLS_RSA_WITH_AES_256_CBC_SHA256',
            'security.ssl3.TLS_RSA_WITH_AES_128_CBC_SHA',
            'security.ssl3.TLS_RSA_WITH_AES_256_CBC_SHA',
            'security.ssl3.TLS_RSA_WITH_3DES_EDE_CBC_SHA'
            
        ]
    #recursive_options = ['default', 'quad9', 'cloudflare', 'google','cleanbrowsing_adult_filter','cleanbrowsing_security_filter']

    # Shuffle the configurations for measurements we want to run
    options = list(itertools.product(recursive_options, dns_options,ciphers))
    random.shuffle(websites)
    for website in websites:
        random.shuffle(options)
        for recursive, dns_type,cipher in options:
            if recursive == 'default' and dns_type in ('doh', 'dot'):
                continue
            if dns_type =='dot' and (recursive == 'opendns_standard' or recursive == 'opendns_family' or recursive == 'libredns_standard' or recursive == 'libredns_adblock'):
                continue
            if dns_type =='dns' and (recursive == 'securedns_standard' or recursive == 'securedns_adblock'):
                continue
            
            run_configuration(log, db, experiment, website,cipher, recursive, dns_type)


def run_configuration(log, db, experiment, website,cipher, recursive, dns_type):
    # Run a measurment for a single website for a given configuration
    resolver_ip = None
    resolver_uri = None
    if recursive == "default":
        resolver_ip = get_default_nameservers()
    else:
        resolver_ip, resolver_uri = Resolvers[recursive].value

    # Collect a HAR, ping time to resolver, and
    # bytes sent/received for a DNS query
    log.info('Collecting {} {} for {} using {}'.format(recursive, dns_type, website,cipher.strip('security.ssl3.')))
    try:
        har, har_uuid, har_error, delays, all_dns_info,tcptimings,webdelays = \
            measure_and_collect_har(log, website, cipher,resolver_ip, resolver_uri, dns_type)

        # Insert HAR, ping times, and DNS timingsinto the db
        neg_cipher=cipher.strip('security.ssl3.')
        rv_har = db.insert_har(experiment, website, neg_cipher, recursive,
                                dns_type,har, har_uuid, har_error, delays,tcptimings,webdelays)
        if not rv_har:
            msg = "Saved HAR for website {}, config: {}, {}, {}"
            log.info(msg.format(website, recursive, dns_type,cipher.strip('security.ssl3.')))
            log.info("Saved delays to resolver for config: {},{}: {}".format(recursive,dns_type,delays))
            log.info("Saved delays to {} for config: {},{}:{}".format(website,recursive,dns_type,webdelays))
            if all_dns_info:
                rv_dns = db.insert_dns(har_uuid, neg_cipher,experiment, recursive, dns_type, all_dns_info)
                if not rv_dns:
                    msg = "Saved DNS timings for website {}"
                    log.info(msg.format(website))
    except Exception as e:
        log.error("Unknown error for website {}: {}".format(website, e))


def measure_and_collect_har(log, website,cipher, resolver_ip, resolver_uri, dns_type):
    # Get a HAR for a website
    website = 'https://{0}'.format(website)
    if dns_type == 'dns':
        dns_opt = "--dns={0}".format(resolver_ip)
        cmd = ['docker', 'run', dns_opt, '--rm','--dns=137.158.152.240', 'tungs/firefox:test-cipher',
                website, cipher, dns_type, 'n/a', 'n/a']
    else:
        cmd = ['docker', 'run', '--rm','--dns=137.158.152.240', 'tungs/firefox:test-cipher',
                website,cipher, dns_type, resolver_ip, resolver_uri]

    # Check if HAR is empty
    try:
        run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        log.error('Error in container for {}:\n{}'.format(website, e.output))
        har = None

    # Decode the output
    try:
        har = run.stdout.decode('utf-8')
        har_error = None
    except Exception as e:
        log.error('Error decoding output for website {}: {}'.format(website, e))
        har_error = run.stderr.decode('utf-8')
        har = None

    # Check if the output is empty
    if not har or har == " ":
        log.error('Output is empty for website: {}'.format(website))
        har = None
        har_error = run.stderr.decode('utf-8')
        json_har = None
    else:
        # Load the HAR as a JSON
        try:
            json_har = json.loads(har)
            for entry in json_har['entries']:
                if 'text' in entry['response']['content']:
                   del entry['response']['content']['text']
            # If zero-bytes remain after stripping content, we remove them.
            # We are removing zero bytes from the JSON file even though they are
            # technically correct because we don't care for the places they can
            # occur and PostgreSQL chokes on them.
            har_reassembled = json.dumps(json_har)
            if "\\u0000" in har_reassembled:
                har_stripped = re.sub(r"(\\)+u0000", "", har_reassembled)
                json_har = json.loads(har_stripped)
        except Exception as e:
            log.error('Error decoding HAR for website: {}\n'.format(website))
            har_error = str(e)
            json_har = None

    # Ping the resolver 5 times
    try:
        delays = ping_resolver(resolver_ip, count=5)
    except:
        log.error('Error pinging resolver: {0}\n'.format(resolver_ip))
        delays = {}

    
    # Ping the resolver 5 times
    try:
       website=website.replace("https://","")
       webdelays = ping_resolver(website, count=5)
    except:
        log.error('Error pinging website: {0}\n'.format(website))
        webdelays = {}

    # Get TCP Timings
    try:
        neg_cipher=cipher.strip('security.ssl3.')
        tcptimings = tcp_timings(website,neg_cipher)
        
    except:
        log.error('Error getting TCP Curl Timings for {0}\n'.format(website))
        delays = {}

    # Create a UUID for the HAR
    har_uuid = uuid.uuid1()

    # Get DNS resolution times for each unique domain in HAR
    try:
        if json_har:
            all_dns_info = measure_dns(website, json_har, har_uuid,
                                       dns_type, resolver_ip, resolver_uri)
        else:
            all_dns_info = None
    except Exception as e:
        log.error('Error getting DNS timings:', str(e))
        all_dns_info = None

    return json_har, har_uuid, har_error, delays, all_dns_info,tcptimings,webdelays


def load_websites(f):
    with open(f, 'r') as ftr:
        websites = [line.strip() for line in ftr]
    return websites


if __name__ == '__main__':
    main()
