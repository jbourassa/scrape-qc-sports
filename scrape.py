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
    td = u''.join(BeautifulSoup(td).findAll(text=True))
    return td
    
def fetch():
    conn = httplib.HTTPConnection('www.ville.quebec.qc.ca', 80)
    conn.request("GET", "/citoyens/loisirs_sports/tennis.aspx")
    response = conn.getresponse()
    html = response.read()

    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    address_tds = soup.findAll("td", attrs={'headers': re.compile('adresse')})

    addresses = [process_td(address) for address in address_tds]
    return addresses

if __name__ == '__main__':
    addresses = fetch()
    with open('tennis.txt', 'w') as f:
        for address in addresses:
            f.write(address.encode('utf-8') + '\n')
