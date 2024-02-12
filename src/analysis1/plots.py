#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import matplotlib as mpl

from collections import namedtuple
from configparser import ConfigParser

sys.path.append('../measure')

from database import DNSDatabase
from pageload import pageload_diffs, pageload_vs_resources,cf_pageloads
from dns_timing import dns_timings, dns_timings_cf, dns_timings_diffs
from latency import dns_pings,dns_pings_cf,dns_pings_diffs
from pageload_cdf import dns_pageloads, dns_pageloads_cf
from common import load_domains


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('database_config_file')
    parser.add_argument('domains_file')
    parser.add_argument('--matplotlibrc', help='custom matplotlibrc')
    parser.add_argument("--cf_pageloads", action='store_true', default=False)
    parser.add_argument("--cf_pageloads_4g_3g", action='store_true', default=False)
    parser.add_argument("--pageload_diffs", action='store_true', default=False)
    parser.add_argument("--dns_timings_diffs", action='store_true', default=False)
    parser.add_argument("--dns_timings_diffs_cleanb_fam", action='store_true', default=False)
    parser.add_argument('--pageload_diffs_cf', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_google', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_quad9', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_cleanb_sec', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_cleanb_fam', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_cleanb_adt', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_adguard_default', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_adguard_family', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_securedns_default', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_securedns_adblock', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_doh', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_dot', action='store_true', default=False)
    parser.add_argument("--pageload_resources", action='store_true', default=False)
    parser.add_argument("--timing", action='store_true', default=False)
    parser.add_argument("--timing_cf", action='store_true', default=False)
    parser.add_argument("--pings", action='store_true', default=False)
    parser.add_argument("--pageload_cdf", action='store_true', default=False)
    parser.add_argument("--name", default=None)
    parser.add_argument("--experiments", default=None, nargs="+")
    args = parser.parse_args()

    # If a custom matplotlibrc is provided, load it
    if args.matplotlibrc:
        mpl.rc_file(args.matplotlibrc)

    # Connect to the db
    db = DNSDatabase.init_from_config_file(args.database_config_file)

    # Load a list of domains to query HARs for
    domains = load_domains(args.domains_file)

    if args.name:
        pageload_diff_filename = "pageload_diff_{}".format(args.name)
        cf_pageloads_filename = "cf_pageloads_{}".format(args.name)
        cf_pageloads_4g_3g_filename = "cf_pageloads_4g_3g{}".format(args.name)
        timings_filename = "dns_timings_{}".format(args.name)
        pings_filename="dns_pings_{}".format(args.name)
        pageload_cdf_filename = "dns_pageloads_{}".format(args.name)
        timings_diff_filename = "dns_timings_diff_{}".format(args.name)
        pageload_resources_filename = "pageload_resources_{}".format(args.name)
        pageloads_subset_filename = "pageload_diff_subset_{}".format(args.name)
    else:
        pageload_diff_filename = "pageload_diff"
        cf_pageloads_filename = "cf_pageloads"
        cf_pageloads_4g_3g_filename = "cf_pageloads_4g_3g"
        timings_filename = "dns_timings"
        pings_filename= "dns_pings"
        pageload_cdf_filename = "dns_pageloads"
        timings_diff_filename = "dns_timings_diff"
        timings_subset_filename = "dns_timings_diff_subset"
        pageload_resources_filename = "pageload_resources"
        pageloads_subset_filename = "pageload_diff_subset"

    # Make plots
    if args.cf_pageloads:
        print("Plotting Cloudflare pageloads")
        cf_pageloads(db, domains, xlimit=10, filename=cf_pageloads_filename,
                     experiments=args.experiments)

    if args.cf_pageloads_4g_3g:
        print("Plotting Cloudflare pageloads (4G lossy and 3G)")
        cf_pageloads_4g_3g(domains, xlimit=30, filename=cf_pageloads_4g_3g_filename,
                           experiments=args.experiments)

    if args.pageload_diffs:
        print("Plotting pageload differences")
        pageload_diffs(db, domains, xlimit=10, filename=pageload_diff_filename,
                       experiments=args.experiments)

    if args.dns_timings_diffs:
        print("Plotting Timings differences")
        dns_timings_diffs(db, domains, xlimit=10, filename=timings_diff_filename,
                       experiments=args.experiments)

    if args.timing:
        print("Plotting DNS timings")
        dns_timings(db, xlimit=650, filename=timings_filename, legend=True,
                    experiments=args.experiments)

    if args.pings:
        print("Plotting Latency")
        dns_pings(db, xlimit=650, filename=pings_filename, legend=True,
                    experiments=args.experiments)

    if args.pageload_cdf:
        print("Plotting Pageload CDFs")
        dns_pageloads(db, domains,xlimit=10, filename=pageload_cdf_filename, legend=True,
                    experiments=args.experiments)

    if args.timing_cf:
        print("Plotting DNS timings")
        dns_timings_cf(db, xlimit=650, filename=timings_filename, legend=True,
                       experiments=args.experiments)

    if args.pageload_resources:
        print("Plotting pageloads vs. resources")
        pageload_vs_resources(db, xlimit=600, filename=pageload_resources_filename,
                              experiments=args.experiments)

    if args.pageload_diffs_cf:
        print("Plotting subset of pageload differences for Cloudflare")
        joint_configs = ('default_dns-cloudflare_dns',
                         'default_dns-cloudflare_dot',
                         'default_dns-cloudflare_doh',
                         'cloudflare_doh-cloudflare_dns',
                         'cloudflare_dot-cloudflare_dns',
                         'cloudflare_dot-cloudflare_doh'
                         )
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.pageload_diffs_google:
        print("Plotting subset of pageload differences for Google")
        joint_configs = ('default_dns-google_dns',
                         'default_dns-google_dot',
                         'default_dns-google_doh',
                         'google_doh-google_dns',
                         'google_dot-google_dns',
                         'google_dot-google_doh'
                         )
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.pageload_diffs_quad9:
        print("Plotting subset of pageload differences for Quad9")
        joint_configs = ('default_dns-quad9_dns',
                         'default_dns-quad9_dot',
                         'default_dns-quad9_doh',
                         'quad9_doh-quad9_dns',
                         'quad9_dot-quad9_dns',
                         'quad9_dot-quad9_doh'
                         )
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)
    
    if args.pageload_diffs_cleanb_sec:
        print("Plotting subset of pageload differences for CleanB-Sec")
        joint_configs = ('cleanbrowsing_security_filter_doh-cleanbrowsing_security_filter_dns',
                         'cleanbrowsing_security_filter_dot-cleanbrowsing_security_filter_dns',
                         'cleanbrowsing_security_filter_dot-cleanbrowsing_security_filter_doh'
                        )
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.pageload_diffs_cleanb_adt:
        print("Plotting subset of pageload differences for CleanB-Adult")
        joint_configs = ('cleanbrowsing_adult_filter_doh-cleanbrowsing_adult_filter_dns',
                         'cleanbrowsing_adult_filter_dot-cleanbrowsing_adult_filter_dns',
                         'cleanbrowsing_adult_filter_dot-cleanbrowsing_adult_filter_doh'
                        )
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.pageload_diffs_cleanb_fam:
        print("Plotting subset of pageload differences for CleanB-Family")
        joint_configs = ('cleanbrowsing_family_filter_doh-cleanbrowsing_family_filter_dns',
                         'cleanbrowsing_family_filter_dot-cleanbrowsing_family_filter_dns',
                         'cleanbrowsing_family_filter_dot-cleanbrowsing_family_filter_doh',
                         'cleanbrowsing_family_filter_dns-cleanbrowsing_security_filter_dns',
                         'cleanbrowsing_family_filter_doh-cleanbrowsing_security_filter_doh',
                         'cleanbrowsing_family_filter_dot-cleanbrowsing_security_filter_dot',
                         'cleanbrowsing_family_filter_dns-cleanbrowsing_adult_filter_dns',
                         'cleanbrowsing_family_filter_dot-cleanbrowsing_adult_filter_dot',
                         'cleanbrowsing_family_filter_doh-cleanbrowsing_adult_filter_doh',
                         'cleanbrowsing_security_filter_dns-cleanbrowsing_adult_filter_dns',
                         'cleanbrowsing_security_filter_dot-cleanbrowsing_adult_filter_dot',
                         'cleanbrowsing_security_filter_doh-cleanbrowsing_adult_filter_doh'

                        )
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.pageload_diffs_adguard_default:
        print("Plotting subset of pageload differences for Adguard_Security")
        joint_configs = ('adguard_default_doh-adguard_default_dns',
                         'adguard_default_dot-adguard_default_dns',
                         'adguard_default_dot-adguard_default_doh',
                         'adguard_default_dns-adguard_family_dns',
                         'adguard_default_dot-adguard_family_dot',
                         'adguard_default_doh-adguard_family_doh'
                        )
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.pageload_diffs_adguard_family:
        print("Plotting subset of pageload differences for Adguard_Family")
        joint_configs = ('adguard_family_doh-adguard_family_dns',
                         'adguard_family_dot-adguard_family_dns',
                         'adguard_family_dot-adguard_family_doh'
                        )
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.pageload_diffs_securedns_default:
        print("Plotting subset of pageload differences for SecureDNS-Security")
        joint_configs = ('securedns_default_dot-securedns_default_doh',
                         'securedns_default_dot-securedns_adblock_dot',
                         'securedns_default_doh-securedns_adblock_doh',
                         'securedns_adblock_doh-securedns_adblock_dot'
                        )
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.dns_timings_diffs_cleanb_fam:
        print("Plotting subset of pageload differences for CleanB-Family")
        joint_configs = ('cleanbrowsing_family_filter_doh-cleanbrowsing_family_filter_dns',
                         'cleanbrowsing_family_filter_dot-cleanbrowsing_family_filter_dns',
                         'cleanbrowsing_family_filter_dot-cleanbrowsing_family_filter_doh',
                         'cleanbrowsing_family_filter_dns-cleanbrowsing_security_filter_dns',
                         'cleanbrowsing_family_filter_doh-cleanbrowsing_security_filter_doh',
                         'cleanbrowsing_family_filter_dot-cleanbrowsing_security_filter_dot',
                         'cleanbrowsing_family_filter_dns-cleanbrowsing_adult_filter_dns',
                         'cleanbrowsing_family_filter_dot-cleanbrowsing_adult_filter_dot',
                         'cleanbrowsing_family_filter_doh-cleanbrowsing_adult_filter_doh',
                         'cleanbrowsing_security_filter_dns-cleanbrowsing_adult_filter_dns',
                         'cleanbrowsing_security_filter_dot-cleanbrowsing_adult_filter_dot',
                         'cleanbrowsing_security_filter_doh-cleanbrowsing_adult_filter_doh'

                        )
        dns_timings_diffs(db, domains, xlimit=10, filename=timings_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    '''
    if args.pageload_diffs_securedns_adblock:
        print("Plotting subset of pageload differences for SecureDNS_Adblock")
        joint_configs = ()
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)
    '''  
    if args.pageload_diffs_doh:
        print("Plotting subset of pageload differences for all DoH providers")
        joint_configs = ('cloudflare_doh-quad9_doh',#(CF,Q9)
                         'cloudflare_doh-google_doh',#(CF,Google)
                         'cloudflare_doh-cleanbrowsing_security_filter_doh',#(CF,CBS)
                         'cloudflare_doh-cleanbrowsing_family_filter_doh', #(CF,CBF)
                         'cloudflare_doh-cleanbrowsing_adult_filter_doh', #(CF,CBA)
                         'cloudflare_doh-adguard_default_doh', #(CF,ADD)
                         'cloudflare_doh-adguard_family_doh', # (AF,ADF)
                         'cloudflare_doh-securedns_default_doh', #(CF,SDD)
                         'cloudflare_doh-securedns_adblock_doh', #(CF,SDA)
                         'google_doh-quad9_doh', #(Google,Q9)
                         'google_doh-cleanbrowsing_security_filter_doh', #(Google,CBS)
                         'google_doh-cleanbrowsing_family_filter_doh', #(Google,CBF)
                         'google_doh-cleanbrowsing_adult_filter_doh', #(Google,CBA)
                         'google_doh-adguard_default_doh', #(Google,ADD)
                         'google_doh-adguard_family_doh', #(Google,ADF)
                         'google_doh-securedns_default_doh', #(Google,SDD)
                         'google_doh-securedns_adblock_doh', #(Google,SDA)
                         'quad9_doh-cleanbrowsing_security_filter_doh', #(Q9,CBS)
                         'quad9_doh-cleanbrowsing_family_filter_doh', #(Q9,CBF)
                         'quad9_doh-cleanbrowsing_adult_filter_doh', #(Q9,CBA)
                         'quad9_doh-adguard_default_doh', #(Q9,ADD)
                         'quad9_doh-adguard_family_doh', #(Q9,ADF)
                         'quad9_doh-securedns_default_doh', #(Q9,SDF)
                         'quad9_doh-securedns_adblock_doh', #(Q9,SDA)
                         'cleanbrowsing_security_filter_doh-cleanbrowsing_family_filter_doh', #(CBS,CBF)
                         'cleanbrowsing_security_filter_doh-cleanbrowsing_adult_filter_doh', #(CBS,CBA)
                         'cleanbrowsing_security_filter_doh-adguard_default_doh', #(CBS,ADD)
                         'cleanbrowsing_security_filter_doh-adguard_family_doh', #(CBS,ADF)
                         'cleanbrowsing_security_filter_doh-securedns_default_doh', #(CBS,SDF)
                         'cleanbrowsing_security_filter_doh-securedns_adblock_doh', #(CBS,SDA)
                         'cleanbrowsing_adult_filter_doh-adguard_default_doh', #(CBA,ADD)
                         'cleanbrowsing_adult_filter_doh-adguard_family_doh', #(CBA,ADF)
                         'cleanbrowsing_adult_filter_doh-securedns_default_doh', #(CBA,SDD)
                         'cleanbrowsing_adult_filter_doh-securedns_adblock_doh', #(CBA,SDA)
                         'cleanbrowsing_family_filter_doh-securedns_default_doh', #CBF,SDD)
                         'cleanbrowsing_family_filter_doh-securedns_adblock_doh', #(CBF,SDA)
                         'cleanbrowsing_family_filter_doh-adguard_default_doh', #(CBF,ADD)
                         'cleanbrowsing_family_filter_doh-adguard_family_doh', #(CBF,ADF)
                         'securedns_default_doh-securedns_adblock_doh', #(SDF,SDA)
                         'securedns_default_doh-securedns_adblock_doh', #(SDD,SDA)
                         'securedns_default_doh-adguard_default_doh', #(SDD,ADD)
                         'securedns_default_doh-adguard_family_doh', # (SDD,ADF)
                         'securedns_adblock_doh-adguard_default_doh', #(SDA,ADD)
                         'securedns_adblock_doh-adguard_family_doh', #(SDA,ADF)
                         'adguard_family_doh-securedns_adblock_doh' #(ADF,SDF)
                        )
        pageload_diffs_doh(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

        if args.pageload_diffs_dot:
            print("Plotting subset of pageload differences for all DoT providers")
            joint_configs = ('cloudflare_dot-quad9_dot',#(CF,Q9)
                            'cloudflare_dot-google_dot',#(CF,Google)
                            'cloudflare_dot-cleanbrowsing_security_filter_dot',#(CF,CBS)
                            'cloudflare_dot-cleanbrowsing_family_filter_dot', #(CF,CBF)
                            'cloudflare_dot-cleanbrowsing_adult_filter_dot', #(CF,CBA)
                            'cloudflare_dot-adguard_default_dot', #(CF,ADD)
                            'cloudflare_dot-adguard_family_dot', # (AF,ADF)
                            'cloudflare_dot-securedns_default_dot', #(CF,SDD)
                            'cloudflare_dot-securedns_adblock_dot', #(CF,SDA)
                            'google_dot-quad9_dot', #(Google,Q9)
                            'google_dot-cleanbrowsing_security_filter_dot', #(Google,CBS)
                            'google_dot-cleanbrowsing_family_filter_dot', #(Google,CBF)
                            'google_dot-cleanbrowsing_adult_filter_dot', #(Google,CBA)
                            'google_dot-adguard_default_dot', #(Google,ADD)
                            'google_dot-adguard_family_dot', #(Google,ADF)
                            'google_dot-securedns_default_dot', #(Google,SDD)
                            'google_dot-securedns_adblock_dot', #(Google,SDA)
                            'quad9_dot-cleanbrowsing_security_filter_dot', #(Q9,CBS)
                            'quad9_dot-cleanbrowsing_family_filter_dot', #(Q9,CBF)
                            'quad9_dot-cleanbrowsing_adult_filter_dot', #(Q9,CBA)
                            'quad9_dot-adguard_default_dot', #(Q9,ADD)
                            'quad9_dot-adguard_family_dot', #(Q9,ADF)
                            'quad9_dot-securedns_default_dot', #(Q9,SDF)
                            'quad9_dot-securedns_adblock_dot', #(Q9,SDA)
                            'cleanbrowsing_security_filter_dot-cleanbrowsing_family_filter_dot', #(CBS,CBF)
                            'cleanbrowsing_security_filter_dot-cleanbrowsing_adult_filter_dot', #(CBS,CBA)
                            'cleanbrowsing_security_filter_dot-adguard_default_dot', #(CBS,ADD)
                            'cleanbrowsing_security_filter_dot-adguard_family_dot', #(CBS,ADF)
                            'cleanbrowsing_security_filter_dot-securedns_default_dot', #(CBS,SDF)
                            'cleanbrowsing_security_filter_dot-securedns_adblock_dot', #(CBS,SDA)
                            'cleanbrowsing_adult_filter_dot-adguard_default_dot', #(CBA,ADD)
                            'cleanbrowsing_adult_filter_dot-adguard_family_dot', #(CBA,ADF)
                            'cleanbrowsing_adult_filter_dot-securedns_default_dot', #(CBA,SDD)
                            'cleanbrowsing_adult_filter_dot-securedns_adblock_dot', #(CBA,SDA)
                            'cleanbrowsing_family_filter_dot-securedns_default_dot', #CBF,SDD)
                            'cleanbrowsing_family_filter_dot-securedns_adblock_dot', #(CBF,SDA)
                            'cleanbrowsing_family_filter_dot-adguard_default_dot', #(CBF,ADD)
                            'cleanbrowsing_family_filter_dot-adguard_family_dot', #(CBF,ADF)
                            'securedns_default_dot-securedns_adblock_dot', #(SDF,SDA)
                            'securedns_default_dot_dot-securedns_adblock_dot', #(SDD,SDA)
                            'securedns_default_dot-adguard_default_dot', #(SDD,ADD)
                            'securedns_default_dot-adguard_family_dot', # (SDD,ADF)
                            'securedns_adblock_dot-adguard_default_dot', #(SDA,ADD)
                            'securedns_adblock_dot-adguard_family_dot', #(SDA,ADF)
                            'adguard_family_dot-securedns_adblock_dot' #(ADF,SDF)
                            )
        pageload_diffs_dot(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

      
    


if __name__ == "__main__":
    main()
