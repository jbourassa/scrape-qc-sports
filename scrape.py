# -*- coding: utf-8 -*-
import httplib
import urllib
import codecs
import json
from BeautifulSoup import BeautifulSoup
import re
import logging

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

class Scraper:
    def __init__(self, domain, url):
        self._domain = domain
        self._url = url

    def scrape(self):
        """Scrapes an url and returns all locations in that html page."""
        html = self._fetch()
        soup = self._soup(html)
        address_tds = soup.findAll("td", attrs={'headers': re.compile('adresse')})
        addresses = [self._process_address_td(address) for address in address_tds]
        return addresses

    def _fetch(self):
        """Makes the HTTP request and returns the response."""
        conn = httplib.HTTPConnection(self._domain, 80)
        conn.request('GET', self._url)
        response = conn.getresponse()
        html = response.read()
        return html

    def _soup(self, html):
        """Returns a BeauifulSoup object from an html string."""
        return BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)

    def _extract_inner_tags(self, tag):
        """Removes all the html tags from a BeautifulSoup tag object."""
        html = u''.join([unicode(text) for text in tag.contents])
        return BeautifulSoup(html)
    
    def _process_tr(self, soup_tr):
        """Process a tr and returns a th for the name,
        td for the address and td for the district."""
        pass
        
    def _process_address_td(self, soup_td):
        """Processes the td containing the address
        and returns an address string."""
        soup_td = self._extract_inner_tags(soup_td)
        rosedesvents = soup_td.find('div', attrs={'id': re.compile('rosedesvents')})
        if rosedesvents is not None: rosedesvents.extract()
        td = re.split('<br\s*/?>', unicode(soup_td))[0]
        td = td.strip()
        address = u''.join(BeautifulSoup(td).findAll(text=True))
        return address

class GeocodingFailureException(Exception): pass
def geocode_address(address):
    """Receives an address and return the lat, lng."""
    address = (u'%s, Québec, Qc, Canada' % address).encode('utf-8')
    conn = httplib.HTTPConnection('maps.googleapis.com', 80)
    conn.request('GET', '/maps/api/geocode/json?%s' % urllib.urlencode({
        'address': address, 'sensor': 'false' }))
    response = conn.getresponse()
    data = json.loads(response.read())
    if data['status'] != 'OK':
        raise GeocodingFailureException('Address not found: %s' % address)
    geometry = data['results'][0]['geometry']
    return geometry['location']['lat'], geometry['location']['lng']


    
if __name__ == '__main__':
    logging.debug('Creating scraper.')
    scraper = Scraper('www.ville.quebec.qc.ca',
                      '/citoyens/loisirs_sports/tennis.aspx')
    addresses = scraper.scrape()
    logging.debug('Got %d addresses.' % len(addresses))
    json_addresses = []
    for address in addresses:
        new_address = {'address': address}
        try:
            logging.debug('Geocoding %s' % address)
            new_address['lat'], new_address['lng'] = geocode_address(address)
        except GeocodingFailureException:
            logging.info('Failed to geocode %s' % address)
        json_addresses.append(new_address)
    with open('tennis.json', 'w') as f:
        f.write(json.dumps(json_addresses).encode('utf-8'))
