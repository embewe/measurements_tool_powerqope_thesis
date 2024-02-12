import argparse
import csv
import json
import subprocess
import sys

import tldextract
import numpy as np

sys.path.append('../measure')
sys.path.append('../analysis')
from database import DNSDatabase
from common import load_domains, get_all_hars

MIN_DNS_HEADER = 12

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('database_config_file')
    parser.add_argument('domains_file')
    args = parser.parse_args()
    
    # Connect to the database for storing HARs
    db = DNSDatabase.init_from_config_file(args.database_config_file)

    # get all individual uuids from har table
    uuidlist = DNSDatabase.get_unique_uuids(db, 'default','dns')
    for uuid in uuidlist:
        domainsseen = {}
        obj_id = 3

        # get the har specific for that uuid
        har = get_har_from_uuid(db,uuid)
        
        # get the sizes specific for that uuid
        dns_sizes = get_sizes_from_uuid(db,uuid)
        
        # get the median delay from the pings held in the har table
        # could also use mean/max/min 
        pagedelay = np.median(har[0]['delays'])
        
        # get the page load time for the har
        plt = get_page_load(har[0])

        # get the HTTP request/response sizes from the har
        size_dict = parse_har(har[0])
        finaloutlist = [] 
        error = False
        for key in size_dict:
            outlist = []
            for i in range(0,len(size_dict[key][0])):
                if key not in domainsseen:
                    if key not in dns_sizes:
                        error = True
                        break
                    if size_dict[key][2] == 0:
                        outlist.append([str(1), 
                                        str(0), 
                                        "DNS", 
                                        str(max(0,dns_sizes[key][2]-pagedelay)), 
                                        str(get_dns_req_size(key)),
                                        str(dns_sizes[key][1])])
                        outlist.append([str(2), 
                                        str(1), 
                                        "HTTP", 
                                        '0.0', 
                                        str(size_dict[key][0][i]),
                                        str(size_dict[key][1][i])])
                        
                        domainsseen[key] = 2
                        obj_id += 1
                    else:
                        outlist.append([str(obj_id), 
                                        str(2), 
                                        "DNS", 
                                        str(max(0,dns_sizes[key][2]-pagedelay)), 
                                        str(get_dns_req_size(key)),
                                        str(dns_sizes[key][1])])
                        domainsseen[key] = obj_id
                        obj_id += 1
                        outlist.append([str(obj_id), 
                                        str(domainsseen[key]), 
                                        "HTTP", 
                                        '0.0', 
                                        str(size_dict[key][0][i]),
                                        str(size_dict[key][1][i])])
                        obj_id += 1
                else:
                    outlist.append([str(obj_id), 
                                    str(domainsseen[key]), 
                                    "HTTP", 
                                    '0.0', 
                                    str(size_dict[key][0][i]),
                                    str(size_dict[key][1][i])])
                    obj_id += 1
            if error:
                break
            else:
                finaloutlist.extend(outlist)
        if error:
            continue
        else:
            with open('temp.rqst', mode='w') as csv_file:
                writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for j in range(0,len(finaloutlist)):
                    writer.writerow(finaloutlist[j])
            output = subprocess.check_output(["make", "runpaul"])
            output = output.decode("utf-8")
            print(output)
            print("PAGE LOAD",plt)

            print(":::::::::::::::::::::::::::::::::")

    

def get_dns_req_size(fqdn):
    query = 5
    for label in fqdn.split('.'):
        query += (1 + len(label))

    return MIN_DNS_HEADER + query

def get_har_from_uuid(self,uuid):
    cmd = '''
            SELECT *
            FROM {}
            WHERE uuid = %s 
          '''.format(self.har_table)
    rv = self._execute_command(cmd,(uuid))
    if rv:
        print('Error getting UUIDs from database, error: {}'.format(rv))
    rv = self.cursor.fetchall()
    return rv

def get_sizes_from_uuid(self,uuid):
    cmd = '''
            SELECT *
            FROM {}
            WHERE har_uuid = %s 
          '''.format(self.dns_table)
    rv = self._execute_command(cmd,(uuid))
    if rv:
        print('Error getting UUIDs from database, error: {}'.format(rv))

    recv = {}
    for (har_uuid, experiment, ins_time, domain, rec, dns_type, resp_size, resp_time, error) in self.cursor.fetchall():
        ext = tldextract.extract(domain)
        domain = ext.domain + "." + ext.suffix
        if ext.subdomain:
            fqdn = ext.subdomain + "." + ext.domain + "." + ext.suffix
        else:
            fqdn = ext.domain + "." + ext.suffix
        domain = fqdn

        recv[domain] = (dns_type, resp_size, resp_time, error)
    return recv

def get_page_load(har_tup):
    har = har_tup['har']
    if not har:
        return []


    if "pages" not in har:
        return None
    pages = har["pages"]

    if len(pages) == 0:
        return None
    page = pages[0]
    pageTimings = page["pageTimings"]

    # onLoad refers to the time it took to load the entire page
    if "onLoad" not in pageTimings:
        return None
    onLoad = pageTimings["onLoad"]

    return(onLoad)


def parse_har(har_tup):
    har = har_tup['har']
    if not har:
        return []

    if "entries" not in har:
        return []
    entries = har["entries"]

    if len(entries) == 0:
        return []

    req_dict = {}
    it = 0
    for entry in entries:
        if "request" not in entry:
            continue
        if "response" not in entry:
            continue
        request = entry["request"]
        response = entry["response"]
       
        reqsize = 0
        respsize = 0

        if 'headersSize' in request:
            reqsize += request['headersSize']
        if 'bodySize' in request:
            reqsize += request['bodySize']

        if 'headersSize' in response:
            respsize += response['headersSize']
        if 'bodySize' in response:
            respsize += response['bodySize']

        if respsize is None or reqsize is None:
            continue
        if "url" not in request:
            continue
        url = request["url"]
        ext = tldextract.extract(url)
        domain = ext.domain + "." + ext.suffix
        if ext.subdomain:
            fqdn = ext.subdomain + "." + ext.domain + "." + ext.suffix
        else:
            fqdn = ext.domain + "." + ext.suffix
        domain = fqdn
        if domain not in req_dict:
            req_dict[domain] = [[],[],it]
            it += 1
        req_dict[domain][0].append(reqsize)
        req_dict[domain][1].append(respsize)

    return req_dict

if __name__ == "__main__":
    main()
