# -*- coding: utf-8 -*-
import httplib
import urllib
import codecs
import json
from BeautifulSoup import BeautifulSoup
import re
import logging

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

PAGES = {
    'skateboard': '/citoyens/loisirs_sports/planche.aspx',
    'sliding': '/citoyens/loisirs_sports/glissoires.aspx',
    'kid_parks': '/citoyens/loisirs_sports/parcs_intergenerationnels.aspx',
    'indoor_skating': '/citoyens/loisirs_sports/patinoires_interieures.aspx',
    'pools': '/citoyens/loisirs_sports/piscines_interieures.aspx',
    'crosscountry_ski': '/citoyens/loisirs_sports/raquettes_ski.aspx',
    'tennis': '/citoyens/loisirs_sports/tennis.aspx'
}

class Scraper:
    def __init__(self, domain):
        self._domain = domain
        self._conn = httplib.HTTPConnection(self._domain, 80)

    def scrape(self, url):
        """Scrapes an url and returns all locations in that html page."""
        logging.debug("Fetching " + url)
        html = self._fetch(url)
        soup = self._soup(html)
        rows = soup.find('table', 'sports').tbody.findAll('tr')
        data = [self._process_tr(row) for row in rows]
        return data

    def _fetch(self, url):
        """Makes the HTTP request and returns the response."""
        self._conn.request('GET', url)
        response = self._conn.getresponse()
        html = response.read()
        return html

    def _soup(self, html):
        """Returns a BeauifulSoup object from an html string."""
        return BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)

    def _extract_inner_tags(self, tag):
        """Removes all the html tags from a BeautifulSoup tag object."""
        html = u''.join([unicode(text) for text in tag.contents])
        return BeautifulSoup(html)
    
    def _process_tr(self, tr):
        """Process a tr and extracts the name and address"""
        address_td = tr.find("td")
        name_th = tr.find("th")
        return {
            'name': re.sub('\s+', ' ', name_th.text),
            'address': self._process_address_td(address_td)
        }
        
    def _process_address_td(self, soup_td):
        """Processes the td containing the address
        and returns an address string."""
        soup_td = self._extract_inner_tags(soup_td)
        rosedesvents = soup_td.find('div', attrs={'id': re.compile('rosedesvents')})
        if rosedesvents is not None: rosedesvents.extract()
        td = soup_td.text
        td = re.split(u'(?i)t(é|e)l', unicode(soup_td))[0]
        td = td.strip()
        address = u''.join(BeautifulSoup(td).findAll(text=True))
        address = re.sub('\s+', ' ', address).strip()
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

def group_activities(activities):
    """Groups activities by location"""
    locations = {} 
    for activity in activities:
        lat_lng = "%f %f" % (activity['lat'], activity['lng'])
        if not lat_lng in locations: locations[lat_lng] = []
        locations[lat_lng].append(activity)

    return locations.values()

if __name__ == '__main__':
    logging.debug('Creating scraper.')
    scraper = Scraper('www.ville.quebec.qc.ca')
    locations = []
    for key, url in PAGES.iteritems():
        page_locations = scraper.scrape(url)
        for location in page_locations:
            locations.append(dict(location, **dict(type=key)))
    
    logging.debug('Got %d locations.' % len(locations))
    
    for location in locations:
        address = location['address']
        try:
            logging.debug('Geocoding %s' % address)
            location['lat'], location['lng'] = geocode_address(address)
        except GeocodingFailureException:
            logging.info('Failed to geocode %s' % address)

    activity_by_location = group_activities(locations)

    with open('locations.json', 'w') as f:
        f.write(json.dumps(activity_by_location).encode('utf-8'))
