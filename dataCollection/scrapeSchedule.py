import requests
import datetime
from bs4 import BeautifulSoup
from baseScrape import Scraper

class EventScraper(Scraper):

    def extract(self):
        """Should get the address and dates"""
        self.name = self._getName()
        self.location = self._getLocation()
        self.addr = self._getAddr()
        self.startDate, self.endDate = self._getDates()
        print(self.startDate, self.endDate)
        
    def _getDates(self):
        urlLi = self.url.split("/")
        for u in urlLi:
            try:
                year = int(u)
            except ValueError:
                pass
        dates = self.soup.findAll('li', attrs={'class': 'dates'})
        date = dates[0].text
        dateLi = date.split(" ")
        mo = dateLi[0]
        days = dateLi[1].split("-")
        start = days[0]
        startStr = "%s-%s-%s" % (year, mo, start)
        startDate = datetime.datetime.strptime(startStr, "%Y-%b-%d")
        end = days[1]
        endStr = "%s-%s-%s" % (year, mo, end)
        endDate = datetime.datetime.strptime(endStr, "%Y-%b-%d")
        return startDate, endDate

    def _getAddr(self):
        tickets = self.soup.findAll('div', attrs={'class': 'sidebar sidebar-event-information'})
        for ticket in tickets:
            addr = ticket.findAll('p')[0].text
            if addr == '':
                addr = None
            print(addr)
            return addr

    def _getName(self):
        names = self.soup.findAll('li', attrs={'class': 'name'})
        for name in names:
            return name.text

    def _getLocation(self):
        locations = self.soup.findAll('li', attrs={'class': 'location'})
        for loc in locations:
            return loc.text

class ScheduleScraper(Scraper):

    def extract(self):
        """Should extract all schedule links"""

        links = self.soup.findAll('a', attrs={'class': 'link-more-info'})
        for link in links:
            if 'schedule' in link['href']:
                es = EventScraper(link['href'])
                es.fetch()
                es.checkAndParse()
                es.extract()
                #es.saveSoupToFile('test_specific.html')

                #es._cleanData()
                self.extracted.append(es)


if __name__ == "__main__":
    ss = ScheduleScraper('schedule')

    ss.fetch()
    ss.checkAndParse()
    ss.extract()

    tokenPath = '__sensitive_apiToken.txt'
    with open(tokenPath) as fi:
        token = fi.read().strip()
    header = {'Authorization': 'Token %s' % (token,)}

    results = []
    for event in ss.extracted:
        print(event)
        new = {}
        new['name'] = event.name
        new['location'] = event.location
        new['schedule_url_slug'] = event.url_slug
        new['address'] = event.addr
        new['start'] = format(event.startDate, '%Y-%m-%d')
        new['end'] = format(event.endDate, '%Y-%m-%d')
        print(new)
        result = requests.post('http://localhost:8000/api/event/', json=new, headers=header)
        results.append(result)

    #ss.saveSoupToFile('test.html')