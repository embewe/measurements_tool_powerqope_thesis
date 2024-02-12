#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import sys
import tldextract
import numpy as np
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import scipy.stats as stats


from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from common import plot_pdf, plot_cdf
from numpy.polynomial.polynomial import polyfit
from common import plot_pdf, plot_cdf, prettify_label

from common import prettify_label

sys.path.append('../measure')
from database import DNSDatabase

def _colorize(ax, dm, shaded=False):
    if not shaded:
        if abs(dm) <= 0.033: # faster
            ax.set_facecolor("white")
        if dm > -0.10 and dm <= -0.033: # slower
            ax.set_facecolor("#d1e5f0")
        if dm > -1.0 and dm <= -0.10: # slower
            ax.set_facecolor("#67a9cfd9")
        if dm <= -1.0: # slower
            ax.set_facecolor("#2166accc")
        if dm < 0.10 and dm >= 0.033:
            ax.set_facecolor("#fddbc7")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xfd/255, 0xdb/255, 0xc7/255, 0.5))
        if dm < 1.0 and dm >= 0.10:
            ax.set_facecolor("#ef8a62d9")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xef/255, 0x8a/255, 0x62/255, 0.5))
        if dm >= 1.0: #
            ax.set_facecolor("#b2182bcc")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xb2/255, 0x18/255, 0x2b/255, 0.5))
    else:
        if abs(dm) <= 0.033: # faster
            ax.set_facecolor("#ffffff40")
        if dm > -0.10 and dm <= -0.033: # slower
            ax.set_facecolor("#d1e5f066")
        if dm > -1.0 and dm <= -0.10: # slower
            ax.set_facecolor("#67a9cf66")
        if dm <= -1.0: # slower
            ax.set_facecolor("#2166ac73")
        if dm < 0.10 and dm >= 0.033:
            ax.set_facecolor("#fddbc7")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xfd/255, 0xdb/255, 0xc7/255, 0.5))
        if dm < 1.0 and dm >= 0.10:
            ax.set_facecolor("#ef8a62bf")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xef/255, 0x8a/255, 0x62/255, 0.5))
        if dm >= 1.0: #
            ax.set_facecolor("#b2182b99")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xb2/255, 0x18/255, 0x2b/255, 0.5))

    return ax



def dns_timings(db, xlimit, filename, legend=False, experiments=None):
    all_recursive_doh_data={
            "default_dns_TLS_RSA_WITH_3DES_EDE_CBC_SHA": {"timings":[], "color":"black", "linestyle":"-","marker":"<", "dashes": ()},
            "cleanbrowsing_family_dot_TLS_RSA_WITH_3DES_EDE_CBC_SHA": {"timings":[], "color":"red", "linestyle":"--","marker":".", "dashes": (5, 5)},
            "cleanbrowsing_family_dot_TLS_DHE_RSA_WITH_AES_256_CBC_SHA256": {"timings":[], "color":"red", "linestyle":"--","marker":"<", "dashes": (5, 1)},
            "cleanbrowsing_family_dot_TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256": {"timings":[], "color":"blue", "linestyle":":","marker":"P", "dashes": (3, 5, 1, 5, 1, 5)},
            "cleanbrowsing_family_dot_TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384": {"timings":[], "color":"blue", "linestyle":":","marker":">", "dashes": (3, 1, 1, 1, 1, 1)},
            "cleanbrowsing_family_dot_TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256": {"timings":[], "color":"green", "linestyle":":","marker":">", "dashes": (3, 5, 1, 5)},
            "cleanbrowsing_family_dot_TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384": {"timings":[], "color":"green", "linestyle":"-.","marker":"^", "dashes": (3, 1, 1, 1)},
            #"securedns_default_doh_4G": {"timings":[], "color":"#696969", "linestyle":"-.","marker":"H", "dashes": (3, 1, 1, 1, 1, 1)},
            
            
    }
    '''
    all_recursive_dot_data={
            "google_dot": {"timings":[], "color":"black", "linestyle":"-","marker":"<"},
            "cloudflare_dot": {"timings":[], "color":"blue", "linestyle":"-","marker":">"},
            "quad9_dot": {"timings":[], "color":"red", "linestyle":"-","marker":"^"},
            "cleanbrowsing_security_filter_dot": {"timings":[], "color":"orange", "linestyle":"-","marker":"."},
            "adguard_default_dot": {"timings":[], "color":"violet", "linestyle":"-","marker":"P"},
            "securedns_default_dot": {"timings":[], "color":"lime", "linestyle":"-","marker":"H"},
           
    }
   
    all_recursive_dns_data={
            "default_dns": {"timings":[], "color":"black", "linestyle":"-","marker":"<"},
            "google_dns": {"timings":[], "color":"blue", "linestyle":"-","marker":"<"},
            "cloudflare_dns": {"timings":[], "color":"red", "linestyle":"-","marker":">"},
            "quad9_dns": {"timings":[], "color":"orange", "linestyle":"-","marker":"^"},
            "cleanbrowsing_security_filter_dns": {"timings":[], "color":"violet", "linestyle":"-","marker":"."},
            "adguard_default_dns": {"timings":[], "color":"lime", "linestyle":"-","marker":"P"},
            
        
    }
    

    
    all_protocols_data={
            "dns_4G": {"timings":[], "color":"#0072B2", "linestyle":"-","marker":"<"},
            "dot_4G": {"timings":[], "color":"#0072B2", "linestyle":":","marker":">"},
            "doh_4G": {"timings":[], "color":"#0072B2", "linestyle":"-.","marker":"^"},
            "dns_3G": {"timings":[], "color":"red", "linestyle":"-","marker":"."},
            "dot_3G": {"timings":[], "color":"red", "linestyle":":","marker":"P"},
            "doh_3G": {"timings":[], "color":"red", "linestyle":"-.","marker":"H"},
        
    }
    all_country_doh_data={
            "doh_4G_ZA": {"timings":[], "color":"#0072B2", "linestyle":"-","marker":"<"},
            "doh_4G_MW": {"timings":[], "color":"red", "linestyle":":","marker":">"},
            "doh_4G_ZM": {"timings":[], "color":"blue", "linestyle":"-.","marker":"^"},
            "doh_4G_UG": {"timings":[], "color":"orange", "linestyle":"-","marker":"."},
            "doh_4G_KE": {"timings":[], "color":"lime", "linestyle":":","marker":"P"},
            "doh_4G_NG": {"timings":[], "color":"violet", "linestyle":"-.","marker":"H"},
            #"quad9_doh_3G_MW": {"timings":[], "color":"indigo", "linestyle":"-"},
            #"quad9_doh_4G_KE": {"timings":[], "color":"green", "linestyle":":"}
            
    }

    all_country_dot_data={
            "dot_4G_ZA": {"timings":[], "color":"#0072B2", "linestyle":"-","marker":"<"},
            "dot_4G_MW": {"timings":[], "color":"red", "linestyle":":","marker":">"},
            "dot_4G_ZM": {"timings":[], "color":"blue", "linestyle":"-.","marker":"^"},
            "dot_4G_UG": {"timings":[], "color":"orange", "linestyle":"-","marker":"."},
            "dot_4G_KE": {"timings":[], "color":"lime", "linestyle":":","marker":"P"},
            "dot_4G_NG": {"timings":[], "color":"violet", "linestyle":"-.","marker":"H"},
           
    }
   
    all_country_dns_data={
            "dns_4G_ZA": {"timings":[], "color":"#0072B2", "linestyle":"-","marker":"<"},
            "dns_4G_MW": {"timings":[], "color":"red", "linestyle":":","marker":">"},
            "dns_4G_ZM": {"timings":[], "color":"blue", "linestyle":"-.","marker":"^"},
            "dns_4G_UG": {"timings":[], "color":"orange", "linestyle":"-","marker":"."},
            "dns_4G_KE": {"timings":[], "color":"lime", "linestyle":":","marker":"P"},
            "dns_4G_NG": {"timings":[], "color":"violet", "linestyle":"-.","marker":"H"},
        
    }

    

    quad9_data = {#"default_dns_Africa": {"timings":[], "color":"#000000", "linestyle":"-"},
            "quad9_dot_Africa": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "quad9_dot_North America": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "quad9_dot_Europe": {"timings":[], "color":"#0072B2", "linestyle":"-."},
            "quad9_doh_Africa": {"timings":[], "color":"red", "linestyle":"-"},
            "quad9_doh_North America": {"timings":[], "color":"red", "linestyle":":"},
            "quad9_doh_Europe": {"timings":[], "color":"red", "linestyle":"-."}}

    cloudflare_data = {#"default_dns": {"timings":[], "color":"#000000", "linestyle":"-"},
            "cloudflare_dot_Africa": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "cloudflare_dot_North America": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "cloudflare_dot_Europe": {"timings":[], "color":"#0072B2", "linestyle":"-."},
            "cloudflare_doh_Africa": {"timings":[], "color":"red", "linestyle":"-"},
            "cloudflare_doh_North America": {"timings":[], "color":"red", "linestyle":":"},
            "cloudflare_doh_Europe": {"timings":[], "color":"red", "linestyle":"-."}}

    google_data = {#"default_dns_Africa": {"timings":[], "color":"#000000", "linestyle":"-"},
            "google_dot_Africa": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "google_dot_North America": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "google_dot_Europe": {"timings":[], "color":"#0072B2", "linestyle":"-."},
            "google_doh_Africa": {"timings":[], "color":"red", "linestyle":"-"},
            "google_doh_North America": {"timings":[], "color":"red", "linestyle":":"},
            "google_doh_Europe": {"timings":[], "color":"red", "linestyle":"-."}}
   
    cleanbrowsing_security_data = {#"default_dns_Africa": {"timings":[], "color":"#000000", "linestyle":"-"},
            "cleanbrowsing_security_filter_dot_Africa": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "cleanbrowsing_security_filter_dot_North America": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "cleanbrowsing_security_filter_dot_Europe": {"timings":[], "color":"#0072B2", "linestyle":"-."},
            "cleanbrowsing_security_filter_doh_Africa": {"timings":[], "color":"red", "linestyle":"-"},
            "cleanbrowsing_security_filter_doh_North America": {"timings":[], "color":"red", "linestyle":":"},
            "cleanbrowsing_security_filter_doh_Europe": {"timings":[], "color":"red", "linestyle":"-."}}

    cleanbrowsing_adult_data = {#"default_dns_Africa": {"timings":[], "color":"#000000", "linestyle":"-"},
            "cleanbrowsing_adult_filter_dot_Africa": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "cleanbrowsing_adult_filter_dot_North America": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "cleanbrowsing_adult_filter_dot_Europe": {"timings":[], "color":"#0072B2", "linestyle":"-."},
            "cleanbrowsing_adult_filter_doh_Africa": {"timings":[], "color":"red", "linestyle":"-"},
            "cleanbrowsing_adult_filter_doh_North America": {"timings":[], "color":"red", "linestyle":":"},
            "cleanbrowsing_adult_filter_doh_Europe": {"timings":[], "color":"red", "linestyle":"-."}}

    cleanbrowsing_family_data = {
            "cleanbrowsing_family_filter_dot_Africa": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "cleanbrowsing_family_filter_dot_North America": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "cleanbrowsing_family_filter_dot_Europe": {"timings":[], "color":"#0072B2", "linestyle":"-."},
            "cleanbrowsing_family_filter_doh_Africa": {"timings":[], "color":"red", "linestyle":"-"},
            "cleanbrowsing_family_filter_doh_North America": {"timings":[], "color":"red", "linestyle":":"},
            "cleanbrowsing_family_filter_doh_Europe": {"timings":[], "color":"red", "linestyle":"-."}}
            

    adguard_default_data = {
            "adguard_default_dot_Africa": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "adguard_default_dot_North America": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "adguard_default_dot_Europe": {"timings":[], "color":"#0072B2", "linestyle":"-."},
            "adguard_default_doh_Africa": {"timings":[], "color":"red", "linestyle":"-"},
            "adguard_default_doh_North America": {"timings":[], "color":"red", "linestyle":":"},
            "adguard_default_doh_Europe": {"timings":[], "color":"red", "linestyle":"-."}}

    adguard_family_data = {#"default_dns_Africa": {"timings":[], "color":"#000000", "linestyle":"-"},
            "adguard_family_dot_Africa": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "adguard_family_dot_North America": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "adguard_family_dot_Europe": {"timings":[], "color":"#0072B2", "linestyle":"-."},
            "adguard_family_doh_Africa": {"timings":[], "color":"red", "linestyle":"-"},
            "adguard_family_doh_North America": {"timings":[], "color":"red", "linestyle":":"},
            "adguard_family_doh_Europe": {"timings":[], "color":"red", "linestyle":"-."}}

    securedns_default_data = {#"default_dns_Africa": {"timings":[], "color":"#000000", "linestyle":"-"},
            "securedns_default_dot_Africa": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "securedns_default_dot_North America": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "securedns_default_dot_Europe": {"timings":[], "color":"#0072B2", "linestyle":"-."},
            "securedns_default_doh_Africa": {"timings":[], "color":"red", "linestyle":"-"},
            "securedns_default_doh_North America": {"timings":[], "color":"red", "linestyle":":"},
            "securedns_default_doh_Europe": {"timings":[], "color":"red", "linestyle":"-."}}

    securedns_adblock_data = {#"default_dns_Africa": {"timings":[], "color":"#000000", "linestyle":"-"},
            "securedns_adblock_dot_Africa": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "securedns_adblock_dot_North America": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "securedns_adblock_dot_Europe": {"timings":[], "color":"#0072B2", "linestyle":"-."},
            "securedns_adblock_doh_Africa": {"timings":[], "color":"red", "linestyle":"-"},
            "securedns_adblock_doh_North America": {"timings":[], "color":"red", "linestyle":":"},
            "securedns_adblock_doh_Euerope": {"timings":[], "color":"red", "linestyle":"-."}}

    '''

    


    # Get DNS timings for each configuration
    timings = db.get_dns_timings(experiments)
    for tup in timings:
        dns_type = tup['dns_type']
        recursive = tup['recursive']
        #network_type=tup['network_type']
        #CountryCode=tup['CountryCode']
        cipher=tup['cipher']
        error = tup['error']
        #config = recursive + "_" + dns_type + "_" + network_type + "_" + CountryCode
        #config = dns_type + "_" + network_type + "_" + CountryCode
        #config = recursive + "_" + network_type + "_" + dns_type
        #config = dns_type + "_" + network_type 
        #config = recursive + "_" + dns_type + "_" + network_type
        config = recursive + "_" + dns_type + '_' + cipher
        response_time = tup['response_time']
        response_size = tup['response_size']
        if error or (response_time == 0 and response_size == 0 and error == 0):
            continue

        '''if config in quad9_data:
            quad9_data[config]['timings'].append(response_time)
        if config in cloudflare_data:
            cloudflare_data[config]['timings'].append(response_time)
        if config in google_data:
            google_data[config]['timings'].append(response_time)
        if config in cleanbrowsing_security_data:
            cleanbrowsing_security_data[config]['timings'].append(response_time)
        if config in cleanbrowsing_family_data:
            cleanbrowsing_family_data[config]['timings'].append(response_time)
        if config in cleanbrowsing_adult_data:
            cleanbrowsing_adult_data[config]['timings'].append(response_time)
        if config in adguard_default_data:
            adguard_default_data[config]['timings'].append(response_time)
        if config in adguard_family_data:
            adguard_family_data[config]['timings'].append(response_time)
        if config in securedns_default_data:
            securedns_default_data[config]['timings'].append(response_time)
        if config in securedns_adblock_data:
            securedns_adblock_data[config]['timings'].append(response_time) 
        if config in all_dns_data:
                all_dns_data[config]['timings'].append(response_time)    
        if config in all_dot_data:
                all_dot_data[config]['timings'].append(response_time) 
        if config in all_doh_data:
                all_doh_data[config]['timings'].append(response_time)
    # Group by country, dns_type, network_type
        if config in all_country_dns_data:
                all_country_dns_data[config]['timings'].append(response_time)
        if config in all_country_dot_data:
                all_country_dot_data[config]['timings'].append(response_time)
        if config in all_country_doh_data:
                all_country_doh_data[config]['timings'].append(response_time)
    # Group by protocol, network type
        if config in all_protocols_data:
                all_protocols_data[config]['timings'].append(response_time)
        if config in all_recursive_dns_data:
                all_recursive_dns_data[config]['timings'].append(response_time)
        if config in all_recursive_dot_data:
                all_recursive_dot_data[config]['timings'].append(response_time)'''
        if config in all_recursive_doh_data:
                all_recursive_doh_data[config]['timings'].append(response_time)
        
        

    # Plot a CDF
    '''plot_dns_timings(quad9_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_quad9.pdf", legend=legend)
    plot_dns_timings(cloudflare_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_cf.pdf", legend=legend)
    plot_dns_timings(google_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_google.pdf", legend=legend)
    plot_dns_timings(cleanbrowsing_security_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_cleanbrowsing_security.pdf", legend=legend)
    plot_dns_timings(cleanbrowsing_family_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_cleanbrowsing_family.pdf", legend=legend)
    plot_dns_timings(cleanbrowsing_adult_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_cleanbrowsing_adult.pdf", legend=legend)
    plot_dns_timings(adguard_default_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_adguard_security.pdf", legend=legend)
    plot_dns_timings(adguard_family_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_adguard_family.pdf", legend=legend)
    plot_dns_timings(securedns_default_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_securedns_security.pdf", legend=legend)
    plot_dns_timings(securedns_adblock_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_securedns_adblock.pdf", legend=legend)
    plot_dns_timings(all_dns_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_all_dns_cdf.pdf", legend=legend)                 
    plot_dns_timings(all_dot_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_all_dot_cdf.pdf", legend=legend) 
    plot_dns_timings(all_doh_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_all_doh_cdf.pdf", legend=legend)
    plot_dns_timings(all_country_dns_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_country_dns_cdf.pdf", legend=legend)
    plot_dns_timings(all_country_dot_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_cocuntry_dot_cdf.pdf", legend=legend)
    plot_dns_timings(all_country_doh_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_country_doh_cdf.pdf", legend=legend)
    # GROUP BY protocols
    plot_dns_timings(all_protocols_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_all_protocols_cdf.pdf", legend=legend)
    #GROUP BY recursive resolver
    plot_dns_timings(all_recursive_dns_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_all_recursive_dns_cdf.pdf", legend=legend)
    plot_dns_timings(all_recursive_dot_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_all_recursive_dot_cdf.pdf", legend=legend)'''
    plot_dns_timings(all_recursive_doh_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_all_recursive_doh_cdf.pdf", legend=legend)
    







def dns_timings_cf(db, xlimit, filename, legend=False, experiments=None):
    cloudflare_data = {"default_dns": {"timings":[], "color":"#000000", "linestyle":"-"},
            "cloudflare_dns": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "cloudflare_doh": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "cloudflare_dot": {"timings":[], "color":"#0072B2", "linestyle":"-."}}

    # Get DNS timings for each configuration
    timings = db.get_dns_timings(experiments)
    for tup in timings:
        dns_type = tup['dns_type']
        recursive = tup['recursive']
        error = tup['error']
        config = recursive + "_" + dns_type
        response_time = tup['response_time']
        response_size = tup['response_size']
        if error or (response_time == 0 and response_size == 0 and error == 0):
            continue

        if config in cloudflare_data:
            cloudflare_data[config]['timings'].append(response_time)

    # Plot a CDF
    plot_dns_timings(cloudflare_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_cf.pdf", legend=legend)


def plot_dns_timings(data, xlimit, bin_step, xlabel, filename, legend=False):
    # Set up the plot
    margin = .033333333
    plt.figure()
    fig, ax = plt.subplots()
    ax.set_xlabel(xlabel, fontsize=15)
    ax.set_ylabel('Probability', fontsize=15)
    ax.set_xlim(- margin * xlimit, xlimit * (1 + margin))
    ax.set_ylim(-0.05, 1.05)
    ax.set_xticks((0, 100, 200, 300, 400, 500, 600,700,800,900,1000))
    plt.xticks(rotation=45)
    

    # Set up the inset plot
    if "3g" in filename:
        ax_ins = inset_axes(ax, width=2.15, height=1.4,
                            loc='lower right', bbox_to_anchor=(375,140))
    else:
        ax_ins = inset_axes(ax, width=2.15, height=1.4,
                            loc='lower right', bbox_to_anchor=(560,75))

    ax_ins.set_xlim(- margin * 2000,
                      2000 * (1 + margin))
    ax_ins.set_ylim(-0.05, 1.05)
    ax_ins.set_xticks((0, 2000))
    ax_ins.set_yticks((0, 1))
    ax_ins.tick_params(axis='both', which='major', labelsize=16)

    for key in sorted(data.keys()):
        # Unpack the data to plot
        d = data[key]
        timings = d["timings"]

        print(key, np.mean(timings), np.std(timings))

        color = d["color"]
        linestyle = d["linestyle"]
        #marker=d["marker"]
        dashes=d['dashes']

        # Plot the data
        sorted_timings = np.sort(timings)
        probs = 1. * np.arange(len(sorted_timings))/(len(sorted_timings) - 1)
        ax.plot(sorted_timings, probs, linewidth=2, color=color,
                linestyle=linestyle, dashes=dashes, label=prettify_label(key))
        ax_ins.plot(sorted_timings, probs, linewidth=2, color=color,
                linestyle=linestyle, dashes=dashes,label=prettify_label(key))

    if legend:
        # ax.legend(loc='center', bbox_to_anchor=(0.5, -0.3), mode='expand', ncol=2, fontsize=16, frameon=False)
        ax.legend(loc='center', bbox_to_anchor=(0.5, -0.45), mode='expand', ncol=2, fontsize=16, frameon=False)
    plt.savefig(filename, bbox_inches='tight')


def dns_timings_diffs(db, domains, xlimit, filename, configs_subset=None, experiments=None):
    all_dns_timings = db.get_dns_timings_domains(domains, experiments)

    configs = ( 'default_dns',
                'quad9_dns',
                'quad9_dot',
                'quad9_doh',
                'google_dns',
                'google_dot',
                'google_doh',
                'cloudflare_dns',
                'cloudflare_dot',
                'cloudflare_doh',
	            'cleanbrowsing_standard_dns',
	            'cleanbrowsing_standard_dot',
	            'cleanbrowsing_standard_doh',
                'cleanbrowsing_family_dns',
	            'cleanbrowsing_family_dot',
	            'cleanbrowsing_family_doh',
                'cleanbrowsing_adult_dns',
	            'cleanbrowsing_adult_dot',
	            'cleanbrowsing_adult_doh'
                'adguard_standard_dns',
                'adguard_standard_dot',
                'adguard_standard_doh',
                'adguard_family_dns',
                'adguard_family_dot',
                'adguard_family_doh',
                'securedns_standard_dns',
                'securedns_standard_dot',
                'securedns_standard_doh',
                'securedns_adblock_dns',
                'securedns_adblock_dot',
                'securedns_adblock_doh'
	          )

    dns_timings_per_experiment = {}
    differences_per_config = {}
    for config in configs:
        for tup in all_dns_timings:
            domain = tup['domain']
            exp = tup['experiment']

            if exp not in dns_timings_per_experiment:
                dns_timings_per_experiment[exp] = {}

            config = tup['recursive'] + '_' + tup['dns_type']
            if config not in dns_timings_per_experiment[exp]:
                dns_timings_per_experiment[exp][config] = {}

            dns_timing = tup['response_time']
            if dns_timing:
                dns_timing = float(dns_timing)
                dns_timings_per_experiment[exp][config][domain] = dns_timing

    for c1 in configs:
        for c2 in configs:
            for exp in dns_timings_per_experiment.keys():
                domains_c1 = dns_timings_per_experiment[exp][c1].keys()
                domains_c2 = dns_timings_per_experiment[exp][c2].keys()
                for domain in (set(domains_c1) & set(domains_c2)):
                    dns_timing_c1 = dns_timings_per_experiment[exp][c1][domain]
                    dns_timing_c2 = dns_timings_per_experiment[exp][c2][domain]

                    joint_configs = c1 + '-' + c2
                    if joint_configs not in differences_per_config:
                        differences_per_config[joint_configs] = []
                    if dns_timing_c1 and dns_timing_c2:
                        if c1 != c2:
                            diff = dns_timing_c1 - dns_timing_c2
                            differences_per_config[joint_configs].append(diff)
                        else:
                            differences_per_config[joint_configs].append(dns_timing_c1)
                            differences_per_config[joint_configs].append(dns_timing_c2)
                    
    # Plot CDFs for each configuration
    all_data = {}
    for joint_configs in differences_per_config:
        differences = differences_per_config[joint_configs]
        color = "#0072B2"
        linestyle = "-"
        data = {"data": differences, "color": color, "linestyle": linestyle}
        all_data[joint_configs] = data

    if configs_subset:
        plot_dns_timings_diffs_subset(all_data, configs_subset, "Page load time (seconds)",
                                   filename + "_cdf.pdf")
    else:  
        plot_dns_timings_diffs(all_data, configs, (10, 10),
                           "DNS Resolution Time (ms)", filename + "_cdf.pdf")

def plot_dns_timings_diffs_subset(all_data, joint_configs, xlabel, filename, experiments=None):
    for key in joint_configs:
        fig, ax = plt.subplots(1, 1)

        data = all_data[key]
        d = data["data"]
        linestyle = data["linestyle"]

        dm = np.median(d)
        ax = _colorize(ax, dm)
        linecolor = 'black'
        meancolor = "#333333"

        sortedd = np.sort(d)
        dp = 1. * np.arange(len(sortedd)) / (len(sortedd) - 1)
        ax.plot(sortedd, dp, color=linecolor, linestyle=linestyle, zorder=2, linewidth=2)
        ax.set_xscale('symlog')
        ax.set_xticklabels(['-10', '-1', '0', '1', '10'], fontsize=16)
        ax.set_yticklabels(['0.0', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=24)
        ax.axvline(x=dm, color=meancolor, linestyle='-', zorder=1, linewidth=1.75)

        c1, c2 = key.split('-', 2)
        ax.set_title("{} - {}".format(prettify_label(c1), prettify_label(c2)), fontsize=20)

        ax.set_xlabel("Page Load Time Difference (seconds)", labelpad=18, fontsize=24)
        ax.set_ylabel("Probability", labelpad=18, fontsize=24)
        plt.savefig(key + "_" + filename, bbox_inches='tight')

    figlegend = plt.figure(figsize=(15.25, 0.55))
    p1 = mpatches.Patch(facecolor="#b2182b", edgecolor="#333333", linewidth=0.25, hatch='......',label='Diff ≥ 1s')
    p2 = mpatches.Patch(facecolor="#ef8a62", edgecolor="#333333", linewidth=0.25, hatch='......',label='0.1s ≤ Diff < 1s')
    p3 = mpatches.Patch(facecolor="#fddbc7", edgecolor="#333333", linewidth=0.25, hatch='......',label='0.03s ≤ Diff < 0.1s')
    p4 = mpatches.Patch(facecolor="#ffffff", edgecolor="#333333", linewidth=0.25, label='-0.03s < Diff < 0.03s')
    p5 = mpatches.Patch(facecolor="#d1e5f0", edgecolor="#333333", linewidth=0.25, label='-0.1s < Diff ≤ -0.03s')
    p6 = mpatches.Patch(facecolor="#67a9cf", edgecolor="#333333", linewidth=0.25, label='-1s < Diff ≤ -0.1s')
    p7 = mpatches.Patch(facecolor="#2166ac", edgecolor="#333333", linewidth=0.25, label='Diff ≤ -1s')
    figlegend.legend(handles = [p1,p2,p3,p4,p5,p6,p7],ncol=7,frameon=False, fontsize=12,handlelength=3, handleheight=2)
    figlegend.savefig('response_time_diff_subset_legend.pdf')
    
    


def plot_dns_timings_diffs(all_data, shape, xlabel, filename,experiments,configs=None):
    # Set up the plots
    fig, axes = plt.subplots(shape[0], shape[1], sharex=True, sharey=True)

    for i in range(shape[0]):
        c1 = configs[i]
        for j in range(shape[1]):
            c2 = configs[j]
            key = c1 + '-' + c2

            data = all_data[key]
            d = data["data"]
            linestyle = data["linestyle"]

            ax = axes[i, j]

            if i == 0:
                # i = row
                ax.set_title("{}\n{}".format(j + 1, prettify_label(c2)), size=4)

            if j == 0:
                # j = column
                ax.set_ylabel("{}\n{}".format(chr(65 + i), prettify_label(c1)),
                              rotation=0, labelpad=18, y=0.33, size=4)

            sortedd = np.sort(d)
            dm = np.median(d)
            mpl.rc('hatch', color='r', linewidth=0.000)

            print(key, dm)

            if j != i:
                # Differences
                if j < i:
                    linecolor = 'black'
                    meancolor = "#333333"
                    ax = _colorize(ax, dm)

                if j > i:
                    ax = _colorize(ax, dm, shaded=True)
                    linecolor = "#00000080"
                    meancolor = "#33333380"

                    for spine in ('top', 'bottom', 'left', 'right'):
                        ax.spines[spine].set_color("lightgray")

                dp = 1. * np.arange(len(sortedd)) / (len(sortedd) - 1)
                ax.plot(sortedd, dp, color=linecolor, linestyle=linestyle, zorder=2, linewidth=0.75)
                ax.set_xscale('symlog')
                ax.set_xticklabels(['-1000', '-10', '0', '10', '1000'])
                ax.axvline(x=dm, color=meancolor, linestyle='--', zorder=1, linewidth=0.5)
            else:
                # Distribution
                linecolor = data["color"]
                meancolor = "gray"
                ax.set_facecolor('#BBBBBB')

    for i in range(shape[0]):
        for j in range(shape[1]):
            if j > i:
                axes[i, j].tick_params(axis='both', color='lightgray')

    p1 = mpatches.Patch(facecolor="#b2182b", edgecolor="#333333", linewidth=0.25, hatch='......',label='x ≥ 1s')
    p2 = mpatches.Patch(facecolor="#ef8a62", edgecolor="#333333", linewidth=0.25, hatch='......',label='0.1s ≤ x < 1s')
    p3 = mpatches.Patch(facecolor="#fddbc7", edgecolor="#333333", linewidth=0.25, hatch='......',label='0.03s ≤ x < 0.1s')
    p4 = mpatches.Patch(facecolor="#ffffff", edgecolor="#333333", linewidth=0.25, label='-0.03s < x < 0.03s')
    p5 = mpatches.Patch(facecolor="#d1e5f0", edgecolor="#333333", linewidth=0.25, label='-0.1s < x ≤ -0.03s')
    p6 = mpatches.Patch(facecolor="#67a9cf", edgecolor="#333333", linewidth=0.25, label='-1s < x ≤ -0.1s')
    p7 = mpatches.Patch(facecolor="#2166ac", edgecolor="#333333", linewidth=0.25, label='x ≤ -1s')

    plt.figlegend(handles = [p7,p6,p5,p4,p3,p2,p1], loc="lower center", ncol=7, frameon=False, fontsize=4, bbox_to_anchor=(0.45, 0.02), handlelength=5, handleheight=4)

    plt.savefig(filename, bbox_inches='tight')
