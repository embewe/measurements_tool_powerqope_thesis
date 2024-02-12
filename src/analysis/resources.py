import sys
import numpy as np
import tldextract
from common import plot_cdf, plot_pdf
sys.path.append('../measure')


def ext_domains(db, domains, xlimit, filename):
    # Get the number of external domains on each page using HARs
    # from the default DNS configuration
    top_k = domains[:1000]
    top_resources = db.get_resources(top_k)
    top_ext_domains = count_ext_domains(top_resources)

    bottom_k = domains[1000:]
    bottom_resources = db.get_resources(bottom_k)
    bottom_ext_domains = count_ext_domains(bottom_resources)

    data = {"Top 1k": {"data": top_ext_domains, "color": "#000000",
                       "linestyle": "-"},
            "99k-100k": {"data": bottom_ext_domains, "color": "#0072B2",
                          "linestyle": "--"}}
    plot_cdf(data, xlimit, 1, "Unique Fully Qualified Domains",
             filename + "_cdf.pdf", ccdf=True, legend_loc='upper right')


def count_ext_domains(resources):
    ext_domains = {}
    for tup in resources:
        har_uuid = tup['uuid']
        domain = tup['domain']

        resource_ext = tldextract.extract(tup['url'])
        website_ext = tldextract.extract(domain)
        resource_sld = resource_ext.domain + "." + resource_ext.suffix
        website_sld = website_ext.domain + '.' + website_ext.suffix
        if resource_ext.subdomain:
            resource_domain = resource_ext.subdomain + "." + resource_sld
        else:
            resource_domain = resource_sld

        if har_uuid not in ext_domains:
            ext_domains[har_uuid] = set()
        ext_domains[har_uuid].add(resource_domain)

    counts = []
    for har_uuid in ext_domains:
        counts.append(len(ext_domains[har_uuid]))
    print(np.median(counts), np.average(counts), np.min(counts), np.max(counts))
    return counts
