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
        elif args.trr_resolver_ip == '94.140.14.14':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "adguard-default.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '94.140.14.15':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "adguard-family.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])
        elif args.trr_resolver_ip == '94.140.14.140':
            subprocess.run(["sudo", "/usr/local/bin/stubby", "-C", "adguard-nofilter.yml", "-g"])
            subprocess.run(["sudo", "cp", "resolv.conf", "/etc/resolv.conf"])

    # Configure the DNS settings in Firefox
    if args.dns_type == 'dns' or args.dns_type == 'dot':
        options.set_preference('network.trr.mode', 0)
    elif args.dns_type == 'doh':
        options.set_preference('network.trr.mode', 3)
        options.set_preference('network.trr.request-timeout', 120000)
        options.set_preference('network.trr.max-fails', 5)
        trr_resolver_ip = args.trr_resolver_ip
        trr_resolver_uri = args.trr_resolver_uri
        if trr_resolver_ip:
            options.set_preference('network.trr.bootstrapAddress', trr_resolver_ip)
        if trr_resolver_uri:
            options.set_preference('network.trr.uri', trr_resolver_uri)

    # Launch Firefox and install our extension for getting HARs
    driver = webdriver.Firefox(options=options,
                               firefox_profile=profile,
                               firefox_binary="/opt/firefox/firefox-bin")
    driver.install_addon("/home/seluser/measure/harexporttrigger-0.6.2-fx.xpi")
    driver.set_page_load_timeout(360)

    # Configure Network Conditions

    '''   def get_network_conditions(self):
       
        return self.execute("getNetworkConditions")['value']

    def set_network_conditions(self, **network_conditions):
      
        driver.set_network_conditions(
                    offline=False,
                    latency=50,  # additional latency (ms)
                    download_throughput=1024 * 1024,  # maximal throughput
                    upload_throughput=1024 * 1024)  # maximal throughput
        self.execute("setNetworkConditions", {
            'network_conditions': network_conditions
        }) '''
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

