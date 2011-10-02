# -*- coding: utf-8 -*-
import httplib
from BeautifulSoup import BeautifulSoup
import re

class Scraper:
    def __init__(self, domain, url):
        self._domain = domain
        self._url = url

    def scrape(self):
        print '1'
        html = self._fetch()
        print '2'
        soup = self._soup(html)
        print '3'
        address_tds = soup.findAll("td", attrs={'headers': re.compile('adresse')})
        print '4'
        addresses = [self._process_td(address) for address in address_tds]
        return addresses

    def _fetch(self):
        conn = httplib.HTTPConnection(self._domain, 80)
        conn.request('GET', self._url)
        response = conn.getresponse()
        html = response.read()
        return html

    def _soup(self, html):
        return BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)

    def _extract_inner_tags(self, tag):
        html = u''.join([unicode(text) for text in tag.contents])
        return BeautifulSoup(html)

    def _process_td(self, soup_td):
        soup_td = self._extract_inner_tags(soup_td)
        rosedesvents = soup_td.find('div', attrs={'id': re.compile('rosedesvents')})
        if rosedesvents is not None: rosedesvents.extract()
        td = re.split('<br\s*/?>', unicode(soup_td))[0]
        td = td.strip()
        address = u''.join(BeautifulSoup(td).findAll(text=True))
        return address

if __name__ == '__main__':
    scraper = Scraper('www.ville.quebec.qc.ca', '/citoyens/loisirs_sports/tennis.aspx')
    addresses = scraper.scrape()

    with open('tennis.txt', 'w') as f:
        for address in addresses:
            f.write(address.encode('utf-8') + '\n')
