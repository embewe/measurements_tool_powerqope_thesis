from bs4 import BeautifulSoup
import re
from collections import defaultdict
import urllib2
import urllib
import csv
import json

ccs = ['Algeria','Angola','Benin','Botswana','Burkina_Faso','Burundi','Cameroon','Cape_Verde','Central_African_Republic',
'Chad','Comoros','Congo','Congo,_Democratic_Republic_of_the','Djibout','Saint_Helene','Egypt','Mauritania',
'Mauritius','Mayote', 'Morocco','Mozambique','Namibia','Niger','Nigeria','Rwanda','Sao_Tome_and_Principe','Senegal',
'Seychelles','Sierra_Leone','Zimbabwe','Zambia','Western_Sahara','Uganda','Tunisia','Tromoeline_Island','Togo','Tanzania',
'Swaziland','Sudan','South_Sudan','South_Africa','Somalia','Mali','Malawi', 'Madagascar','Libya','Liberia','Lesotho','Kenya',
'Guenea-Bissau','Guinea','Ghana','Gambia','Gabon', 'Ethiopia','Eritrea','Equatorial_Guinea']

ALEXA_URL = "https://www.alexa.com/topsites/category/Top/Regional/Africa/"

f = open("data/topafrica.csv","w")
print "cc|domain|"

for cc in ccs:
    url = ALEXA_URL + cc
    
    try:
        res = urllib2.urlopen(url)
	print "Processing " + url
    except Exception, e:
        print url + " Not found"
    #except urllib2.HTTPError, e:
    #    print e.code
    #except urllib2.URLError, e:
    #    print e.args
        
    soup = BeautifulSoup(res, "html.parser")
    mydivs = soup.findAll("div", {"class": "tr site-listing"})
    
    for div in mydivs:
        rank = div.findAll("div", {"class": "td number"})
        site = div.findAll('a')
        tdrightdiv = div.findAll("div", {"class": "td right"})
        row =  cc + "," + site[0].text + "\n"
        f.write(row)
        
f.close()
print "done"
