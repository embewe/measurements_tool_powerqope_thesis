#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os.path
import sys
import time
import subprocess
import shutil

from datetime import datetime
from enum import Enum

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('website')
    parser.add_argument('cipher_level')
    parser.add_argument('dns_type', choices=['dns', 'doh', 'dot'])
    parser.add_argument('trr_resolver_ip')
    parser.add_argument('trr_resolver_uri')
    parser.add_argument('--timeout', type=int, default=90)
    args = parser.parse_args()

        ## Specify ciphers
    high=['security.ssl3.TLS_AES_256_GCM_SHA384',
        'security.ssl3.TLS_CHACHA20_POLY1305_SHA256',
        'security.ssl3.ECDHE-ECDSA-AES256-GCM-SHA384',
        'security.ssl3.ECDHE-RSA-AES256-GCM-SHA384',
        'security.ssl3.DHE-DSS-AES256-GCM-SHA384',
        'security.ssl3.DHE-RSA-AES256-GCM-SHA384',
        'security.ssl3.ECDHE-ECDSA-CHACHA20-POLY1305',
        'security.ssl3.ECDHE-RSA-CHACHA20-POLY1305',
        'security.ssl3.DHE-RSA-CHACHA20-POLY1305',
        'security.ssl3.ECDHE-ECDSA-AES256-CCM8',
        'security.ssl3.ECDHE-ECDSA-AES256-CCM',
        'security.ssl3.DHE-RSA-AES256-CCM8',
        'security.ssl3.DHE-RSA-AES256-CCM',
        'security.ssl3.ECDHE-ECDSA-ARIA256-GCM-SHA384',
        'security.ssl3.ECDHE-ARIA256-GCM-SHA384',
        'security.ssl3.DHE-DSS-ARIA256-GCM-SHA384',
        'security.ssl3.DHE-RSA-ARIA256-GCM-SHA384',
        'security.ssl3.ECDHE-ECDSA-AES256-SHA384',
        'security.ssl3.ECDHE-RSA-AES256-SHA384',
        'security.ssl3.DHE-RSA-AES256-SHA256',
        'security.ssl3.DHE-DSS-AES256-SHA256'
    ]

    medium=['security.ssl3.TLS_AES_128_GCM_SHA256',
            'security.ssl3.RSA-PSK-AES256-GCM-SHA384',
            'security.ssl3.DHE-PSK-AES256-GCM-SHA384',
            'security.ssl3.RSA-PSK-CHACHA20-POLY1305',
            'security.ssl3.DHE-PSK-CHACHA20-POLY1305',
            'security.ssl3.ECDHE-PSK-CHACHA20-POLY1305',
            'security.ssl3.DHE-PSK-AES256-CCM8',
            'security.ssl3.DHE-PSK-AES256-CCM',
            'security.ssl3.RSA-PSK-ARIA256-GCM-SHA384',
            'security.ssl3.DHE-PSK-ARIA256-GCM-SHA384',
            'security.ssl3.AES256-GCM-SHA384',
            'security.ssl3.AES256-CCM8',
            'security.ssl3.AES256-CCM',
            'security.ssl3.ARIA256-GCM-SHA384',
            'security.ssl3.PSK-AES256-GCM-SHA384',
            'security.ssl3.PSK-CHACHA20-POLY1305',
            'security.ssl3.PSK-AES256-CCM8',
            'security.ssl3.PSK-AES256-CCM',
            'security.ssl3.PSK-ARIA256-GCM-SHA384',
            'security.ssl3.AES256-SHA256',
            'security.ssl3.CAMELLIA256-SHA256',
        ]

    low=[ 'security.ssl3.ECDHE-ECDSA-AES128-GCM-SHA256',
            'security.ssl3.ECDHE-RSA-AES128-GCM-SHA256',
            'security.ssl3.DHE-DSS-AES128-GCM-SHA256',
            'security.ssl3.DHE-RSA-AES128-GCM-SHA256',
            'security.ssl3.ECDHE-ECDSA-AES128-CCM8',
            'security.ssl3.ECDHE-ECDSA-AES128-CCM',
            'security.ssl3.DHE-RSA-AES128-CCM8',
            'security.ssl3.DHE-RSA-AES128-CCM',
            'security.ssl3.ECDHE-ECDSA-ARIA128-GCM-SHA256',
            'security.ssl3.ECDHE-ARIA128-GCM-SHA256',
            'security.ssl3.DHE-DSS-ARIA128-GCM-SHA256',
            'security.ssl3.DHE-RSA-ARIA128-GCM-SHA256',
            'security.ssl3.ECDHE-ECDSA-AES128-SHA256',
            'security.ssl3.ECDHE-RSA-AES128-SHA256',
            'security.ssl3.DHE-RSA-AES128-SHA256',
            'security.ssl3.DHE-DSS-AES128-SHA256',
            'security.ssl3.ECDHE-ECDSA-CAMELLIA128-SHA256',
            'security.ssl3.ECDHE-RSA-CAMELLIA128-SHA256',
            'security.ssl3.DHE-RSA-CAMELLIA128-SHA256',
            'security.ssl3.DHE-DSS-CAMELLIA128-SHA256',
            'security.ssl3.RSA-PSK-AES128-GCM-SHA256',
            'security.ssl3.DHE-PSK-AES128-GCM-SHA256',
            'security.ssl3.DHE-PSK-AES128-CCM8',
            'security.ssl3.DHE-PSK-AES128-CCM',
            'security.ssl3.RSA-PSK-ARIA128-GCM-SHA256',
            'security.ssl3.DHE-PSK-ARIA128-GCM-SHA256',
            'security.ssl3.AES128-GCM-SHA256',
            'security.ssl3.AES128-CCM8',
            'security.ssl3.AES128-CCM',
            'security.ssl3.ARIA128-GCM-SHA256',
            'security.ssl3.PSK-AES128-GCM-SHA256',
            'security.ssl3.PSK-AES128-CCM8',
            'security.ssl3.PSK-AES128-CCM',
            'security.ssl3.PSK-ARIA128-GCM-SHA256',
            'security.ssl3.AES128-SHA256',
            'security.ssl3.CAMELLIA128-SHA256'
    ]

    # Enable devtools in Firefox
    options = Options()
    options.headless = True
    options.add_argument('-devtools')

    # Enable the netmonitor toolbox in devtools so we can save HARs
    profile = webdriver.FirefoxProfile()
    profile.set_preference('devtools.toolbox.selectedTool', 'netmonitor')

    # If we're running a DoT measurement, turn on Stubby
    if args.dns_type == 'dot':
        if args.trr_resolver_ip == '1.1.1.1':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "stubby-cf.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '1.1.1.2':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "stubby-cf-security.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '1.1.1.3':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "stubby-cf-family.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '9.9.9.9':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "stubby-quad9.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '9.9.9.10':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "stubby-quad9_nofilter.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '9.9.9.11':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "quad9_security_edns.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '8.8.8.8':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "stubby-google.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '185.228.168.9':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "cleanb-family.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '185.228.168.10':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "cleanb-adult.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '185.228.168.168':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "cleanb-security.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '146.185.167.43':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "securedns-adblock.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '176.103.130.131':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "adguard-default.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '176.103.130.132':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "adguard-family.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '176.103.130.136':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "adguard-nofilter.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])

    # Configure the DNS settings in Firefox
    if args.dns_type == 'dns' or args.dns_type == 'dot':
        options.set_preference('network.trr.mode', 0)
        # Define Ciphersuites (Do53/DoT)
        cipher_level=args.cipher_level
        if cipher_level=='high':
            for cipher_high in high:
                options.set_preference(cipher_high,	True) 
        elif cipher_level=='medium':
            for cipher_medium in medium:
                options.set_preference(cipher_medium,	True) 
        elif cipher_level=='low':
            for cipher_low in low:
                options.set_preference(cipher_low,	True) 
    elif args.dns_type == 'doh':
        options.set_preference('network.trr.mode', 3)
        options.set_preference('network.trr.request-timeout', 1500)
        options.set_preference('network.trr.max-fails', 5)
        trr_resolver_ip = args.trr_resolver_ip
        trr_resolver_uri = args.trr_resolver_uri
        if trr_resolver_ip:
            options.set_preference('network.trr.bootstrapAddress', trr_resolver_ip)
        if trr_resolver_uri:
            options.set_preference('network.trr.uri', trr_resolver_uri)
         # Define Ciphersuites (DoH)
        cipher_level=args.cipher_level
        if cipher_level=='high':
            for cipher_high in high:
                options.set_preference(cipher_high,	True) 
        elif cipher_level=='medium':
            for cipher_medium in medium:
                options.set_preference(cipher_medium,	True) 
        elif cipher_level=='low':
            for cipher_low in low:
                options.set_preference(cipher_low,	True) 
       
    
    # Launch Firefox and install our extension for getting HARs
    driver = webdriver.Firefox(options=options,
                               firefox_profile=profile,
                               firefox_binary="/opt/firefox/firefox-bin")
    driver.install_addon("/home/seluser/measure/harexporttrigger-0.6.2-fx.xpi")
    driver.set_page_load_timeout(120)


    # Make a page load
    started = datetime.now()
    driver.get(args.website)

    # Once the HAR is on disk in the container, write it to stdout so the host machine can get it
    har_file = "/home/seluser/measure/har.json"
    def har_file_ready():
        return os.path.exists(har_file + ".ready")

    while (datetime.now() - started).total_seconds() < args.timeout \
            and not har_file_ready():
        time.sleep(1)

    if har_file_ready():
        with open(har_file, 'rb') as f:
            sys.stdout.buffer.write(f.read())
    driver.quit()


if __name__ == '__main__':
    main()
