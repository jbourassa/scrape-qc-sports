# -*- coding: utf-8 -*-
import httplib
from BeautifulSoup import BeautifulSoup
import re

def extract_inner_tags(tag):
    html = u''.join([unicode(text) for text in tag.contents])
    return BeautifulSoup(html)

def process_td(soup_td):
    soup_td = extract_inner_tags(soup_td)
    rosedesvents = soup_td.find('div', attrs={'id': re.compile('rosedesvents')})
    if rosedesvents is not None: rosedesvents.extract()
    td = re.split('<br\s*/?>', unicode(soup_td))[0]
    td = td.strip()
    td = u' '.join(BeautifulSoup(td).findAll(text=True))
    return td
    
def unmess_html_plz(html):
    return html.replace('‑','-')

conn = httplib.HTTPConnection('www.ville.quebec.qc.ca', 80)
conn.request("GET", "/citoyens/loisirs_sports/tennis.aspx")
response = conn.getresponse()
html = response.read()

soup = BeautifulSoup(unmess_html_plz(html))
address_tds = soup.findAll("td", attrs={'headers': re.compile('adresse')})

addresses = [process_td(address) for address in address_tds]

for address in  addresses: print address
