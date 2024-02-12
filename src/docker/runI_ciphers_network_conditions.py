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
    parser.add_argument('cipher')
    parser.add_argument('network_type')
    parser.add_argument('dns_type', choices=['dns', 'doh', 'dot'])
    parser.add_argument('trr_resolver_ip')
    parser.add_argument('trr_resolver_uri')
    parser.add_argument('--timeout', type=int, default=30)
    args = parser.parse_args()

    # Enable devtools in Firefox
    options = Options()
    options.headless = True
    options.add_argument('-devtools')

    # Enable the netmonitor toolbox in devtools so we can save HARs
    profile = webdriver.FirefoxProfile()
    profile.set_preference('devtools.toolbox.selectedTool', 'netmonitor')

    #Clear Cache
    profile.set_preference('browser.cache.disk.enable', False)
    profile.set_preference('browser.cache.memory.enable', False)
    profile.set_preference('browser.cache.offline.enable', False)
    profile.set_preference('network.cookie.cookieBehavior', 2)


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
    cipher=args.cipher
    if args.dns_type == 'dns' or args.dns_type == 'dot':
        options.set_preference('network.trr.mode', 0)
        # Define Ciphersuites    
        options.set_preference(cipher,	True) 
    elif args.dns_type == 'doh':
        options.set_preference('network.trr.mode', 3)
        options.set_preference('network.trr.request-timeout', 1500)
        options.set_preference('network.trr.max-fails', 5)
        trr_resolver_ip = args.trr_resolver_ip
        trr_resolver_uri = args.trr_resolver_uri
        options.set_preference(cipher,	True)
        if trr_resolver_ip:
            options.set_preference('network.trr.bootstrapAddress', trr_resolver_ip)
        if trr_resolver_uri:
            options.set_preference('network.trr.uri', trr_resolver_uri)

     
    # Launch Firefox and install our extension for getting HARs
    driver = webdriver.Firefox(options=options,
                               firefox_profile=profile,
                               firefox_binary="/opt/firefox/firefox-bin")
    driver.install_addon("/home/seluser/measure/harexporttrigger-0.6.2-fx.xpi")
    driver.set_page_load_timeout(120)

# configure network conditions
    K = 1024
    M = 1024 * 1024
    Bps = 1 / 8
    KBps = K * Bps
    MBps = M * Bps
    if args.network_type=='3G':
        def get_network_conditions(self):

           return self.execute("getNetworkConditions")['value']

        def set_network_conditions(self, **network_conditions):

            driver.set_network_conditions(
                        offline=False,
                        download_throughput= 750 * KBps,
                        upload_throughput= 250 * KBps,
                        latency= 500)
            self.execute("setNetworkConditions", {
                'network_conditions': network_conditions
            })
    elif args.network_type=='4G':
        def get_network_conditions(self):
    
           return self.execute("getNetworkConditions")['value']

        def set_network_conditions(self, **network_conditions):

            driver.set_network_conditions(
                        offline=False,
                        download_throughput= 4 * MBps,
                        upload_throughput= 3 * MBps,
                        latency= 350)
            self.execute("setNetworkConditions", {
                'network_conditions': network_conditions
            })
    elif args.network_type=='DSL':
        def get_network_conditions(self):
    
           return self.execute("getNetworkConditions")['value']

        def set_network_conditions(self, **network_conditions):

            driver.set_network_conditions(
                        offline=False,
                        download_throughput= 2 * MBps,
                        upload_throughput= 1 * MBps,
                        latency= 200)
            self.execute("setNetworkConditions", {
                'network_conditions': network_conditions
            })
    elif args.network_type=='wifi':
        def get_network_conditions(self):
    
           return self.execute("getNetworkConditions")['value']

        def set_network_conditions(self, **network_conditions):

            driver.set_network_conditions(
                       offline=False,
                        download_throughput= 30 * MBps,
                        upload_throughput= 15 * MBps,
                        latency= 100)
            self.execute("setNetworkConditions", {
                'network_conditions': network_conditions
            })
    elif args.network_type=='default':
        def get_network_conditions(self):
    
           return self.execute("getNetworkConditions")['value']

        def set_network_conditions(self, **network_conditions):

            driver.set_network_conditions(
                        offline=False,
                        latency=0,  # additional latency (ms)
                        download_throughput=-1,  # maximal throughput
                        upload_throughput=-1)  # maximal throughput
            self.execute("setNetworkConditions", {
                'network_conditions': network_conditions
            })


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
