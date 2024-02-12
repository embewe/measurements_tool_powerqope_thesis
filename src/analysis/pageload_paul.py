#!/usr/bin/env python#
# -*- coding: utf-8 -*-

import json
import argparse
import sys

import tldextract
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import scipy.stats as stats

sys.path.append('../measure')

from database import DNSDatabase
from common import plot_pdf, plot_cdf
from numpy.polynomial.polynomial import polyfit
from common import plot_pdf, plot_cdf, prettify_label


raise Exception("OUTDATED! DO NOT USE pageload_paul")


def plot_pageload_cdfs(hars, xlimit, filename):
    # Get page load timings for each configuration
    default_dns_pageloads = get_all_onLoads(hars["default_dns"])
    quad9_dns_pageloads = get_all_onLoads(hars["quad9_dns"])
    quad9_doh_pageloads = get_all_onLoads(hars["quad9_doh"])
    quad9_dot_pageloads = get_all_onLoads(hars["quad9_dot"])
    cf_dns_pageloads = get_all_onLoads(hars["cf_dns"])
    cf_doh_pageloads = get_all_onLoads(hars["cf_doh"])
    cf_dot_pageloads = get_all_onLoads(hars["cf_dot"])
    google_dns_pageloads = get_all_onLoads(hars["google_dns"])
    google_doh_pageloads = get_all_onLoads(hars["google_doh"])
    google_dot_pageloads = get_all_onLoads(hars["google_dot"])

    # Plot a CDF
    data = {"Default (DNS)": {"data": default_dns_pageloads,
                              "color": "black", "linestyle": "-"},
            "Quad9 (DNS)": {"data": quad9_dns_pageloads,
                            "color": "#0072B2", "linestyle": "-"},
            "Quad9 (DoH)": {"data": quad9_doh_pageloads,
                            "color": "#0072B2", "linestyle": ":"},
            "Quad9 (DoT)": {"data": quad9_dot_pageloads,
                            "color": "#0072B2", "linestyle": "-."},
            "Cloudflare (DNS)": {"data": cf_dns_pageloads,
                                 "color": "#e79f00", "linestyle": "-"},
            "Cloudflare (DoH)": {"data": cf_doh_pageloads,
                                 "color": "#e79f00", "linestyle": ":"},
            "Cloudflare (DoT)": {"data": cf_dot_pageloads,
                                 "color": "#e79f00", "linestyle": "-."},
            "Google (DNS)": {"data": google_dns_pageloads,
                                 "color": "#e79f00", "linestyle": "-"},
            "Google (DoH)": {"data": google_doh_pageloads,
                                 "color": "#e79f00", "linestyle": ":"},
            "Google (DoT)": {"data": google_dot_pageloads,
                                 "color": "#e79f00", "linestyle": "-."}}
    plot_cdf(data, xlimit, 0.1, "Page load time (seconds)",
             filename + "_cdf.pdf")
    plot_pdf(data, "Page load time (seconds)",
             filename + "_pdf.pdf")


def pageload_vs_resources(db, xlimit, filename):
    pageloads_resources = db.get_resource_counts()

    # Get pageloads for each resource count for DNS, DoH, and DoT
    data = {}
    for tup in pageloads_resources:
        dns_type = tup['dns_type']
        resources = tup['resources']
        pageload = tup['pageload']

        if not dns_type or not resources or not pageload or pageload <= 0:
            continue

        if dns_type not in data:
            data[dns_type] = {'x': [], 'y': []}
        data[dns_type]['x'].append(resources)
        data[dns_type]['y'].append(pageload / 1000)

    # Make a scatterplot
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim(right=xlimit)
    for dns_type in data:
        x = data[dns_type]['x']
        y = data[dns_type]['y']
        b, m = polyfit(x, y, 1)
        print(b, m)

        if dns_type == 'dns':
            color = 'red'
            zorder = 2
        if dns_type == 'dot':
            color = 'blue'
            zorder = 1
        if dns_type == 'doh':
            color = 'black'
            zorder = 0

        ax.scatter(x, y, s=5,
                   zorder=zorder, c=color, label=dns_type)

        fit_y = [(b + m * x_val) for x_val in x]
        ax.plot(x, fit_y, color=color)
    plt.legend(loc='lower right')
    plt.savefig(filename)


def pageload_diffs(db, domains, xlimit, filename, configs_subset=None):
    # Get all pageloads from the db
    all_pageloads = db.get_pageloads(domains)
    configs = ('default_dns',
               'quad9_dns',
               'quad9_dot',
               'quad9_doh',
               'google_dns',
               'google_dot',
               'google_doh',
               'cloudflare_dns',
               'cloudflare_dot',
               'cloudflare_doh')


    pageloads_per_experiment = {}
    differences_per_config = {}
    for config in configs:
        for tup in all_pageloads:
            domain = tup['domain']
            exp = tup['experiment']

            if exp not in pageloads_per_experiment:
                pageloads_per_experiment[exp] = {}

            config = tup['recursive'] + '_' + tup['dns_type']
            if config not in pageloads_per_experiment[exp]:
                pageloads_per_experiment[exp][config] = {}

            pageload = tup['pageload']
            if pageload:
                pageload = float(pageload) / 1000.
                pageloads_per_experiment[exp][config][domain] = pageload

    for c1 in configs:
        for c2 in configs:
            for exp in pageloads_per_experiment.keys():
                domains_c1 = pageloads_per_experiment[exp][c1].keys()
                domains_c2 = pageloads_per_experiment[exp][c2].keys()
                for domain in (set(domains_c1) & set(domains_c2)):
                    pageload_c1 = pageloads_per_experiment[exp][c1][domain]
                    pageload_c2 = pageloads_per_experiment[exp][c2][domain]

                    joint_configs = c1 + '-' + c2
                    if joint_configs not in differences_per_config:
                        differences_per_config[joint_configs] = []
                    if pageload_c1 and pageload_c2:
                        if c1 != c2:
                            diff = pageload_c1 - pageload_c2
                            differences_per_config[joint_configs].append(diff)
                        else:
                            differences_per_config[joint_configs].append(pageload_c1)
                            differences_per_config[joint_configs].append(pageload_c2)

    # Plot CDFs for each configuration
    all_data = {}
    for joint_configs in differences_per_config:
        differences = differences_per_config[joint_configs]
        color = "#0072B2"
        linestyle = "-"
        data = {"data": differences, "color": color, "linestyle": linestyle}
        all_data[joint_configs] = data

    if configs_subset:
        plot_pageload_diffs_subset(all_data, configs_subset,
                                   "Page load time (seconds)",
                                   filename + "_cdf.pdf")
    else:
        plot_pageload_diffs(all_data, configs, (10, 10),
                            "Page load time (seconds)",
                            filename + "_cdf.pdf")


def plot_pageload_diffs_subset(all_data, joint_configs, xlabel, filename):
    for key in joint_configs:
        fig, ax = plt.subplots(1, 1)

        data = all_data[key]
        d = data["data"]
        color = data["color"]
        linestyle = data["linestyle"]

        sortedd = np.sort(d)
        dmean = np.mean(d)

        # Differences
        dp = 1. * np.arange(len(sortedd)) / (len(sortedd) - 1)

        if abs(dmean) <= 0.033: # faster
            ax.set_facecolor("white")
        if dmean > -0.10 and dmean <= -0.033: # slower
            ax.set_facecolor("#d1e5f0")
        if dmean > -1.0 and dmean <= -0.10: # slower
            ax.set_facecolor("#67a9cfd9")
        if dmean <= -1.0: # slower
            ax.set_facecolor("#2166accc")
        if dmean < 0.10 and dmean >= 0.033:
            ax.set_facecolor("#fddbc7")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch=".",
                            edgecolor=(0xfd/255, 0xdb/255, 0xc7/255, 0.5))
        if dmean < 1.0 and dmean >= 0.10:
            ax.set_facecolor("#ef8a62d9")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch=".",
                            edgecolor=(0xef/255, 0x8a/255, 0x62/255, 0.5))
        if dmean >= 1.0: #
            ax.set_facecolor("#b2182bcc")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch=".",
                            edgecolor=(0xb2/255, 0x18/255, 0x2b/255, 0.5))

        linecolor = 'black'
        meancolor = "#333333"

        ax.plot(sortedd, dp, color=linecolor, linestyle=linestyle, zorder=2, linewidth=2)
        ax.set_xscale('symlog')
        ax.set_xticklabels(['-10', '-1', '0', '1', '10'], fontsize=24)
        ax.set_yticklabels(['0.0', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=24)
        ax.axvline(x=dmean, color=meancolor, linestyle='-', zorder=1, linewidth=1.75)

        # Set up the labels and save the figure
        ax.set_xlabel("Page Load Time Difference (seconds)", labelpad=18, fontsize=24)
        ax.set_ylabel("Probability", labelpad=18, fontsize=24)
        if "doh" in key:
            plt.savefig("doh" + filename, bbox_inches='tight')
        elif "dot" in key:
            plt.savefig("dot" + filename, bbox_inches='tight')


    # Save the legend to a separate image
    figlegend = plt.figure(figsize=(15.25, 0.55))
    p1 = mpatches.Patch( facecolor="#b2182b",edgecolor="#333333",linewidth=0.01,hatch='......',label='Diff <= -1s')
    p2 = mpatches.Patch( facecolor="#ef8a62",edgecolor="#333333",linewidth=0.01,hatch='......',label='-1s < Diff <= -0.1s')
    p3 = mpatches.Patch( facecolor="#fddbc7",edgecolor="#333333",linewidth=0.01,hatch='......',label='-0.1s < Diff <= -0.03s')
    p4 = mpatches.Patch( facecolor="#ffffff",edgecolor="#333333",linewidth=0.01,label='-0.03s < Diff < 0.03s')
    p5 = mpatches.Patch( facecolor="#d1e5f0",edgecolor="#333333",linewidth=0.01,label='0.03s <= Diff < 0.1s')
    p6 = mpatches.Patch( facecolor="#67a9cf",edgecolor="#333333",linewidth=0.01,label='0.1s <= Diff < 1s')
    p7 = mpatches.Patch( facecolor="#2166ac",edgecolor="#333333",linewidth=0.01,label='Diff >= 1s')
    figlegend.legend(handles = [p1,p2,p3,p4,p5,p6,p7],ncol=7,frameon=False, fontsize=12,handlelength=3, handleheight=2)
    figlegend.savefig('pageload_diff_subset_legend.pdf')


def plot_pageload_diffs(all_data, configs, shape, xlabel, filename):
    # Set up the plots
    fig, axes = plt.subplots(shape[0], shape[1], sharex=True, sharey=True)

    for i in range(shape[0]):
        c1 = configs[i]
        for j in range(shape[1]):
            c2 = configs[j]
            key = c1 + '-' + c2

            data = all_data[key]
            d = data["data"]
            color = data["color"]
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
            dmean = np.mean(d)
            mpl.rc('hatch', color='r', linewidth=0.000)


            if j != i:
                # Differences
                dp = 1. * np.arange(len(sortedd)) / (len(sortedd) - 1)
                if j < i:
                    if abs(dmean) <= 0.033: # faster
                        ax.set_facecolor("white")
                    if dmean > -0.10 and dmean <= -0.033: # slower
                        ax.set_facecolor("#d1e5f0")
                    if dmean > -1.0 and dmean <= -0.10: # slower
                        ax.set_facecolor("#67a9cfd9")
                    if dmean <= -1.0: # slower
                        ax.set_facecolor("#2166accc")
                    if dmean < 0.10 and dmean >= 0.033:
                        ax.set_facecolor("#fddbc7")
                        ax.fill_between([-40,40],-0.05,1.05,
                                        facecolor="none",
                                        linewidth=0.0,
                                        hatch="......",
                                        edgecolor=(0xfd/255, 0xdb/255, 0xc7/255, 0.5))
                    if dmean < 1.0 and dmean >= 0.10:
                        ax.set_facecolor("#ef8a62d9")
                        ax.fill_between([-40,40],-0.05,1.05,
                                        facecolor="none",
                                        linewidth=0.0,
                                        hatch="......",
                                        edgecolor=(0xef/255, 0x8a/255, 0x62/255, 0.5))
                    if dmean >= 1.0: #
                        ax.set_facecolor("#b2182bcc")
                        ax.fill_between([-40,40],-0.05,1.05,
                                        facecolor="none",
                                        linewidth=0.0,
                                        hatch="......",
                                        edgecolor=(0xb2/255, 0x18/255, 0x2b/255, 0.5))

                    linecolor = 'black'
                    meancolor = "#333333"

                if j > i:
                    if abs(dmean) <= 0.033: # faster
                        ax.set_facecolor("#ffffff40")
                    if dmean > -0.10 and dmean <= -0.033: # slower
                        ax.set_facecolor("#d1e5f066")
                    if dmean > -1.0 and dmean <= -0.10: # slower
                        ax.set_facecolor("#67a9cf66")
                    if dmean <= -1.0: # slower
                        ax.set_facecolor("#2166ac73")
                    if dmean < 0.10 and dmean >= 0.033:
                        ax.set_facecolor("#fddbc7")
                        ax.fill_between([-40,40],-0.05,1.05,
                                        facecolor="none",
                                        linewidth=0.0,
                                        hatch="......",
                                        edgecolor=(0xfd/255, 0xdb/255, 0xc7/255, 0.5))
                    if dmean < 1.0 and dmean >= 0.10:
                        ax.set_facecolor("#ef8a62bf")
                        ax.fill_between([-40,40],-0.05,1.05,
                                        facecolor="none",
                                        linewidth=0.0,
                                        hatch="......",
                                        edgecolor=(0xef/255, 0x8a/255, 0x62/255, 0.5))
                    if dmean >= 1.0: #
                        ax.set_facecolor("#b2182b99")
                        ax.fill_between([-40,40],-0.05,1.05,
                                        facecolor="none",
                                        linewidth=0.0,
                                        hatch="......",
                                        edgecolor=(0xb2/255, 0x18/255, 0x2b/255, 0.5))
                    #if dmean < -0.0: # faster
                    #    ax.set_facecolor((0x46/255, 0x78/255, 0x21/255, min(0.25, abs(dmean))))
                    #if dmean > 0.0: # slower
                    #    ax.set_facecolor((0xA6/255, 0x06/255, 0x28/255, min(0.25, dmean)))
                    linecolor = "#00000080"
                    meancolor = "#33333380"
                    for spine in ('top', 'bottom', 'left', 'right'):
                        ax.spines[spine].set_color("lightgray")

                ax.plot(sortedd, dp, color=linecolor, linestyle=linestyle, zorder=2, linewidth=0.75)
                ax.set_xscale('symlog')
                # ax.set_yscale('symlog')
                ax.set_xticklabels(['-10', '-1', '0', '1', '10'])
                ax.axvline(x=dmean, color=meancolor, linestyle='--', zorder=1, linewidth=0.5)
            else:
                # Distribution
                linecolor = data["color"]
                meancolor = "gray"
                ax.set_facecolor('#BBBBBB')

                #hist, bins = np.histogram(d, 1000)
                #ax.plot(d, pdf, color=color, linestyle=linestyle)

    for i in range(shape[0]):
        for j in range(shape[1]):
            if j > i:
                axes[i, j].tick_params(axis='both', color='lightgray')


    # Create the legend for the plot
    p1 = mpatches.Patch( facecolor="#b2182b",edgecolor="#333333",linewidth=0.01,hatch='......',label='x <= -1s')
    p2 = mpatches.Patch( facecolor="#ef8a62",edgecolor="#333333",linewidth=0.01,hatch='......',label='-1s < x <= -0.1s')
    p3 = mpatches.Patch( facecolor="#fddbc7",edgecolor="#333333",linewidth=0.01,hatch='......',label='-0.1s < x <= -0.03s')
    p4 = mpatches.Patch( facecolor="#ffffff",edgecolor="#333333",linewidth=0.01,label='-0.03s < x < 0.03s')
    p5 = mpatches.Patch( facecolor="#d1e5f0",edgecolor="#333333",linewidth=0.01,label='0.03s <= x < 0.1s')
    p6 = mpatches.Patch( facecolor="#67a9cf",edgecolor="#333333",linewidth=0.01,label='0.1s <= x < 1s')
    p7 = mpatches.Patch( facecolor="#2166ac",edgecolor="#333333",linewidth=0.01,label='x >= 1s')
    ax.legend(handles=[p1,p2,p3,p4,p5,p6,p7],loc="center",ncol=7,frameon=False, fontsize=3.5,bbox_to_anchor=[-5, -1],handlelength=5, handleheight=4)

    # Set up the labels/legend
    plt.savefig(filename, bbox_inches='tight')
