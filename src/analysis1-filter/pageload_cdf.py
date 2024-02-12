#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import division
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



def dns_pageloads(db, domains,xlimit, filename, legend=False, experiments=None):
    cleanbrowsing_family_data = {"default_dns": {"pageloads":[], "color":"#000000", "linestyle":"-"},
            "cleanbrowsing_security_filter_dns": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
            "cleanbrowsing_security_filter_doh": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
            "cleanbrowsing_security_filter_dot": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
            "cleanbrowsing_adult_filter_dns": {"pageloads":[], "color":"red", "linestyle":"-"},
            "cleanbrowsing_adult_filter_doh": {"pageloads":[], "color":"red", "linestyle":":"},
            "cleanbrowsing_adult_filter_dot": {"pageloads":[], "color":"red", "linestyle":"-."},
            "cleanbrowsing_family_filter_dns": {"pageloads":[], "color":"purple", "linestyle":"-"},
            "cleanbrowsing_family_filter_doh": {"pageloads":[], "color":"purple", "linestyle":":"},
            "cleanbrowsing_family_filter_dot": {"pageloads":[], "color":"purple", "linestyle":"-."}}

    quad9_dns = {"default_dns": {"pageloads":[], "color":"#000000", "linestyle":"-"},
            "quad9_nofilter_dns": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
            "quad9_nofilter_doh": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
            "quad9_nofilter_dot": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
            "quad9_security_dns": {"pageloads":[], "color":"red", "linestyle":"-"},
            "quad9_security_doh": {"pageloads":[], "color":"red", "linestyle":":"},
            "quad9_security_dot": {"pageloads":[], "color":"red", "linestyle":"-."}}

    cloudflare_dns = {"default_dns": {"pageloads":[], "color":"#000000", "linestyle":"-"},
            "cloudflare_nofilter_dns": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
            "cloudflare_nofilter_doh": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
            "cloudflare_nofilter_dot": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
            "cloudflare_security_dns": {"pageloads":[], "color":"red", "linestyle":"-"},
            "cloudflare_security_doh": {"pageloads":[], "color":"red", "linestyle":":"},
            "cloudflare_security_dot": {"pageloads":[], "color":"red", "linestyle":"-."},
            "cloudflare_family_dns": {"pageloads":[], "color":"purple", "linestyle":"-"},
            "cloudflare_family_doh": {"pageloads":[], "color":"purple", "linestyle":":"},
            "cloudflare_family_dot": {"pageloads":[], "color":"purple", "linestyle":"-."}
            }

    adguard_default_data = {"default_dns": {"pageloads":[], "color":"#000000", "linestyle":"-"},
            "adguard_nofilter_dns": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
            "adguard_nofilter_doh": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
            "adguard_nofilter_dot": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
            "adguard_adblock_dns": {"pageloads":[], "color":"red", "linestyle":"-"},
            "adguard_adblock_doh": {"pageloads":[], "color":"red", "linestyle":":"},
            "adguard_adblock_dot": {"pageloads":[], "color":"red", "linestyle":"-."},
            "adguard_family_dns": {"pageloads":[], "color":"purple", "linestyle":"-"},
            "adguard_family_doh": {"pageloads":[], "color":"purple", "linestyle":":"},
            "adguard_family_dot": {"pageloads":[], "color":"purple", "linestyle":"-."}}
    
    # quad9_dot = {#"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "quad9_dot_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
    #         "quad9_dot_North America": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
    #         "quad9_dot_Europe": {"pageloads":[], "color":"#0072B2", "linestyle":"-."}}

    # quad9_doh = {#"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "quad9_doh_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
    #         "quad9_doh_North America": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
    #         "quad9_doh_Europe": {"pageloads":[], "color":"#0072B2", "linestyle":"-."}}

    
    # cloudflare_dot = {#"default_dns": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "cloudflare_dot_Africa": {"pageloads":[], "color":"red", "linestyle":"-"},
    #         "cloudflare_dot_North America": {"pageloads":[], "color":"red", "linestyle":":"},
    #         "cloudflare_dot_Europe": {"pageloads":[], "color":"red", "linestyle":"-."}}

    # cloudflare_doh = {#"default_dns": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "cloudflare_doh_Africa": {"pageloads":[], "color":"red", "linestyle":"-"},
    #         "cloudflare_doh_North America": {"pageloads":[], "color":"red", "linestyle":":"},
    #         "cloudflare_doh_Europe": {"pageloads":[], "color":"red", "linestyle":"-."}}

    # google_dns = {#"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "google_dns_Africa": {"pageloads":[], "color":"green", "linestyle":"-"},
    #         "google_dns_North America": {"pageloads":[], "color":"green", "linestyle":":"},
    #         "google_dns_Europe": {"pageloads":[], "color":"green", "linestyle":"-."}}

    # google_dot = {#"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "google_dot_Africa": {"pageloads":[], "color":"green", "linestyle":"-"},
    #         "google_dot_North America": {"pageloads":[], "color":"green", "linestyle":":"},
    #         "google_dot_Europe": {"pageloads":[], "color":"green", "linestyle":"-."}}

    # google_doh = {#"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "google_doh_Africa": {"pageloads":[], "color":"green", "linestyle":"-"},
    #         "google_doh_North America": {"pageloads":[], "color":"green", "linestyle":":"},
    #         "google_doh_Europe": {"pageloads":[], "color":"green", "linestyle":"-."}}
   
    # cleanbrowsing_security_data = {#"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "cleanbrowsing_security_filter_dot_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
    #         "cleanbrowsing_security_filter_dot_North America": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
    #         "cleanbrowsing_security_filter_dot_Europe": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
    #         "cleanbrowsing_security_filter_doh_Africa": {"pageloads":[], "color":"red", "linestyle":"-"},
    #         "cleanbrowsing_security_filter_doh_North America": {"pageloads":[], "color":"red", "linestyle":":"},
    #         "cleanbrowsing_security_filter_doh_Europe": {"pageloads":[], "color":"red", "linestyle":"-."}}

    # cleanbrowsing_adult_data = {#"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "cleanbrowsing_adult_filter_dot_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
    #         "cleanbrowsing_adult_filter_dot_North America": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
    #         "cleanbrowsing_adult_filter_dot_Europe": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
    #         "cleanbrowsing_adult_filter_doh_Africa": {"pageloads":[], "color":"red", "linestyle":"-"},
    #         "cleanbrowsing_adult_filter_doh_North America": {"pageloads":[], "color":"red", "linestyle":":"},
    #         "cleanbrowsing_adult_filter_doh_Europe": {"pageloads":[], "color":"red", "linestyle":"-."}}

    # adguard_family_data = {#"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "adguard_family_dot_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
    #         "adguard_family_dot_North America": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
    #         "adguard_family_dot_Europe": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
    #         "adguard_family_doh_Africa": {"pageloads":[], "color":"red", "linestyle":"-"},
    #         "adguard_family_doh_North America": {"pageloads":[], "color":"red", "linestyle":":"},
    #         "adguard_family_doh_Europe": {"pageloads":[], "color":"red", "linestyle":"-."}}

    # securedns_default_data = {#"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "securedns_default_dot_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
    #         "securedns_default_dot_North America": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
    #         "securedns_default_dot_Europe": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
    #         "securedns_default_doh_Africa": {"pageloads":[], "color":"red", "linestyle":"-"},
    #         "securedns_default_doh_North America": {"pageloads":[], "color":"red", "linestyle":":"},
    #         "securedns_default_doh_Europe": {"pageloads":[], "color":"red", "linestyle":"-."}}

    # securedns_adblock_data = {#"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
    #         "securedns_adblock_dot_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
    #         "securedns_adblock_dot_North America": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
    #         "securedns_adblock_dot_Europe": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
    #         "securedns_adblock_doh_Africa": {"pageloads":[], "color":"red", "linestyle":"-"},
    #         "securedns_adblock_doh_North America": {"pageloads":[], "color":"red", "linestyle":":"},
    #         "securedns_adblock_doh_Euerope": {"pageloads":[], "color":"red", "linestyle":"-."}}

    # all_dot_data={
            
    #         "quad9_dot_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
    #         "quad9_dot_North America": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
    #         "quad9_dot_Europe": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
    #         "cloudflare_dot_Africa": {"pageloads":[], "color":"red", "linestyle":"-"},
    #         "cloudflare_dot_North America": {"pageloads":[], "color":"red", "linestyle":":"},
    #         "cloudflare_dot_Europe": {"pageloads":[], "color":"red", "linestyle":"-."},
    #         "google_dot_Africa": {"pageloads":[], "color":"green", "linestyle":"-"},
    #         "google_dot_North America": {"pageloads":[], "color":"green", "linestyle":":"},
    #         "google_dot_Europe": {"pageloads":[], "color":"green", "linestyle":"-."},
           
    # }

    # all_doh_data={
    #         "quad9_doh_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
    #         "quad9_doh_North America": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
    #         "quad9_doh_Europe": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
    #         "cloudflare_doh_Africa": {"pageloads":[], "color":"red", "linestyle":"-"},
    #         "cloudflare_doh_North America": {"pageloads":[], "color":"red", "linestyle":":"},
    #         "cloudflare_doh_Europe": {"pageloads":[], "color":"red", "linestyle":"-."},
    #         "google_doh_Africa": {"pageloads":[], "color":"green", "linestyle":"-"},
    #         "google_doh_North America": {"pageloads":[], "color":"green", "linestyle":":"},
            
    # }

    # all_dns_data={
    #         "quad9_dns_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
    #         "quad9_dns_North America": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
    #         "quad9_dns_Europe": {"pageloads":[], "color":"#0072B2", "linestyle":"-."},
    #         "cloudflare_dns_Africa": {"pageloads":[], "color":"red", "linestyle":"-"},
    #         "cloudflare_dns_North America": {"pageloads":[], "color":"red", "linestyle":":"},
    #         "cloudflare_dns_Europe": {"pageloads":[], "color":"red", "linestyle":"-."},
    #         "google_dns_Africa": {"pageloads":[], "color":"green", "linestyle":"-"},
    #         "google_dns_North America": {"pageloads":[], "color":"green", "linestyle":":"},
    #         "google_dns_Europe": {"pageloads":[], "color":"green", "linestyle":"-."}
        
    # }


    # Get DNS pageloads for each configuration
    pageloads = db.get_pageloads(domains, experiments)
    pageloads_per_config = {}

    for tup in pageloads:
        config = tup['recursive'] + '_' + tup['dns_type']
        if config not in pageloads_per_config:
            pageloads_per_config[config] = []
        
        pageload = tup['pageload']
        if pageload:
            pageload = float(pageload) /1000
     
        if (pageload == None):
            continue

        if config in quad9_dns:
            quad9_dns[config]['pageloads'].append(pageload)
        # if config in quad9_dot:
        #     quad9_dot[config]['pageloads'].append(pageload)
        # if config in quad9_doh:
        #     quad9_doh[config]['pageloads'].append(pageload)
        if config in cloudflare_dns:
            cloudflare_dns[config]['pageloads'].append(pageload)
        # if config in cloudflare_dot:
        #     cloudflare_dot[config]['pageloads'].append(pageload)
        # if config in cloudflare_doh:
        #     cloudflare_doh[config]['pageloads'].append(pageload)
        # if config in google_dns:
        #     google_dns[config]['pageloads'].append(pageload)
        # if config in google_dot:
        #     google_dot[config]['pageloads'].append(pageload)
        # if config in google_doh:
        #     google_doh[config]['pageloads'].append(pageload)
        # if config in cleanbrowsing_security_data:
        #     cleanbrowsing_security_data[config]['pageloads'].append(pageload)
        if config in cleanbrowsing_family_data:
            cleanbrowsing_family_data[config]['pageloads'].append(pageload)
        # if config in cleanbrowsing_adult_data:
        #     cleanbrowsing_adult_data[config]['pageloads'].append(pageload)
        if config in adguard_default_data:
            adguard_default_data[config]['pageloads'].append(pageload)
        # if config in adguard_family_data:
        #     adguard_family_data[config]['pageloads'].append(pageload)
        # if config in securedns_default_data:
        #     securedns_default_data[config]['pageloads'].append(pageload)
        # if config in securedns_adblock_data:
        #     securedns_adblock_data[config]['pageloads'].append(pageload)
        # if config in all_dot_data:
        #         all_dot_data[config]['pageloads'].append(pageload)
        # if config in all_doh_data:
        #         all_doh_data[config]['pageloads'].append(pageload)
        # if config in all_dns_data:
        #         all_dns_data[config]['pageloads'].append(pageload)
        

    # Plot a CDF
    plot_dns_pageloads(quad9_dns, xlimit, 1, "DNS Response Time (seconds)",
                     filename + "_quad9_dns_cdf.pdf", legend=legend)
    # plot_dns_pageloads(quad9_dot, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_quad9_dot_cdf.pdf", legend=legend)
    # plot_dns_pageloads(quad9_doh, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_quad9_doh_cdf.pdf", legend=legend)               
    plot_dns_pageloads(cloudflare_dns, xlimit, 1, "DNS Response Time (seconds)",
                     filename + "_cf_dns_cdf.pdf", legend=legend)
    # plot_dns_pageloads(cloudflare_dot, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_cf_dot_cdf.pdf", legend=legend)
    # plot_dns_pageloads(cloudflare_doh, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_cf_doh_cdf.pdf", legend=legend)
    # plot_dns_pageloads(google_dns, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_google_dns_cdf.pdf", legend=legend)
    # plot_dns_pageloads(google_dot, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_google_dot_cdf.pdf", legend=legend)
    # plot_dns_pageloads(google_doh, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_google_doh_cdf.pdf", legend=legend)
    # plot_dns_pageloads(cleanbrowsing_security_data, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_cleanbrowsing_security.pdf", legend=legend)
    plot_dns_pageloads(cleanbrowsing_family_data, xlimit, 1, "DNS Response Time (seconds)",
                     filename + "_cleanbrowsing_family.pdf", legend=legend)
    # plot_dns_pageloads(cleanbrowsing_adult_data, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_cleanbrowsing_adult.pdf", legend=legend)
    plot_dns_pageloads(adguard_default_data, xlimit, 1, "DNS Response Time (seconds)",
                     filename + "_adguard_security.pdf", legend=legend)
    # plot_dns_pageloads(adguard_family_data, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_adguard_family.pdf", legend=legend)
    # plot_dns_pageloads(securedns_default_data, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_securedns_security.pdf", legend=legend)
    # plot_dns_pageloads(securedns_adblock_data, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_securedns_adblock.pdf", legend=legend)
    # plot_dns_pageloads(all_dot_data, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_all_dot_cdf.pdf", legend=legend)
    # plot_dns_pageloads(all_doh_data, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_all_doh_cdf.pdf", legend=legend)
    # plot_dns_pageloads(all_dns_data, xlimit, 1, "DNS Response Time (seconds)",
    #                  filename + "_all_dns_cdf.pdf", legend=legend)
    





# def dns_pageloads_cf(db, xlimit, filename, legend=False, experiments=None):
#     cloudflare_data = {"default_dns_Africa": {"pageloads":[], "color":"#000000", "linestyle":"-"},
#             "cloudflare_dns_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-"},
#             "cloudflare_doh_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":":"},
#             "cloudflare_dot_Africa": {"pageloads":[], "color":"#0072B2", "linestyle":"-."}}

#     # Get DNS pageloads for each configuration
#     pageloads = db.get_dns_pageloads(experiments)
#     for tup in pageloads:
#         dns_type = tup['dns_type']
#         recursive = tup['recursive']
#         #error = tup['error']
#         config = recursive + "_" + dns_type
#         pageload = float(tup['pageload']) / 1000
#         #response_size = tup['response_size']
#         if (pageload == 0):
#             continue

#         if config in cloudflare_data:
#             cloudflare_data[config]['pageloads'].append(pageload)

#     # Plot a CDF
#     plot_dns_pageloads(cloudflare_data, xlimit, 1, "DNS Response Time (seconds)",
#                      filename + "_cf.pdf", legend=legend)


def plot_dns_pageloads(data, xlimit, bin_step, xlabel, filename, legend=False):
    # Set up the plot
    margin = .033333333
    plt.figure()
    fig, ax = plt.subplots()
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel('Probability', fontsize=15)
    ax.set_xlim(- margin * xlimit, xlimit * (1 + margin))
    ax.set_ylim(-0.05, 1.05)
    ax.set_xticks((0, 1, 2, 3, 4, 5))
    plt.xticks(rotation=0)
    

    # Set up the inset plot
    if "3g" in filename:
        ax_ins = inset_axes(ax, width=2.15, height=1.4,
                            loc='lower right', bbox_to_anchor=(375,140))
    else:
        ax_ins = inset_axes(ax, width=2.15, height=1.4,
                            loc='lower right', bbox_to_anchor=(560,75))

    ax_ins.set_xlim(- margin * 10,
                      10 * (1 + margin))
    ax_ins.set_ylim(-0.05, 1.05)
    ax_ins.set_xticks((0, 10))
    ax_ins.set_yticks((0, 1))
    ax_ins.tick_params(axis='both', which='major', labelsize=10)

    for key in sorted(data.keys()):
        # Unpack the data to plot
        d = data[key]
        pageloads = d["pageloads"]

        print(key, np.mean(pageloads), np.std(pageloads))

        color = d["color"]
        linestyle = d["linestyle"]

        # Plot the data
        sorted_pageloads = np.sort(pageloads)
        probs = 1. * np.arange(len(sorted_pageloads))/(len(sorted_pageloads) - 1)
        ax.plot(sorted_pageloads, probs, linewidth=1.5, color=color,
                linestyle=linestyle, label=prettify_label(key))
        ax_ins.plot(sorted_pageloads, probs, linewidth=1.5, color=color,
                    linestyle=linestyle, label=prettify_label(key))

    if legend:
        # ax.legend(loc='center', bbox_to_anchor=(0.5, -0.3), mode='expand', ncol=2, fontsize=16, frameon=False)
        ax.legend(loc='center', bbox_to_anchor=(0.5, -0.45), mode='expand', ncol=2, fontsize=15, frameon=False)
    plt.savefig(filename, bbox_inches='tight')


