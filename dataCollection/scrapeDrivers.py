import requests
import datetime
import csv
from bs4 import BeautifulSoup
from baseScrape import Scraper

class DriverScraper(Scraper):

    def extract(self):

        summaries = self.soup.findAll('div', attrs={'class': 'driver-summary'})
        for summary in summaries:
            self.name = self._getName(summary)
            print("NAME", self.name)
            self.info = self._getInfo(summary)
            print(self.info)
        self.ranks = self._getRanks()
        print(self.ranks)

    def _getRanks(self):
        ranks = self.soup.findAll('div', attrs={'class': 'driver-rank'})
        for rank in ranks:
            categoryLi = []
            categories = rank.findAll('div', attrs={'class': 'category'})
            for category in categories:
                categoryLi.append(category.text.strip())
            rankLi = []
            rankDetails = rank.findAll('div', attrs={'class': 'rank'})
            for rankDetail in rankDetails:
                rankLi.append(rankDetail.text.strip())
            pointDetails = rank.findAll('div', attrs={'class': 'points'})
            for pointDetail in pointDetails:
                temp = pointDetail.text.strip()
                try:
                    temp = int(temp)
                except ValueError:
                    temp = None
                rankLi.append(temp)

        rankDic = {}
        for c, category in enumerate(categoryLi):
            try:
                test = rankDic[category]
                print("Duplicate keys in ranks: %s" % (category,))
            except KeyError:
                rankDic[category] = rankLi[c]
        return rankDic

    def _getName(self, summary):
        name = summary.findAll('h1', attrs={'class': 'driver-name'})
        name = name[0].text.replace("Rookie", "")
        return name

    def _getInfo(self, summary):
        infoDict = {}
        infoSections = summary.findAll('li', attrs={'class': 'information'})
        for info in infoSections:
            infoLi = info.text.split(": ")
            try:
                test = infoDict[infoLi[0].strip()]
                print("Duplicate key")
            except KeyError:
                infoDict[infoLi[0].strip()] = infoLi[1].strip()
        return infoDict

    def postData(self, base="http://localhost:8000/", pro2=False, tokenPath='__sensitive_apiToken.txt'):
        print(f"Posting data: {self.__dict__}")
        with open(tokenPath) as fi:
            token = fi.read().strip()
        header = {'Authorization': 'Token %s' % (token,)}
        to_post = {
            'name': self.name,
            'team_name': self.info['Team Name'],
            'driver_url_slug': self.url_slug,
            'car_number': self.info['Car Number'],
            'car_manuf': self.info['Car Manufacturer'],
            'pro2': pro2
            }
        check = requests.get(
            base + 'api/racer/',
            json={"driver_url_slug": self.url_slug},
            headers=header
        )
        if check.status_code == 200:
            matching = check.json()
            if len(matching) > 0:
                result = matching[0]
                return result
        result = requests.post(
            base + 'api/racer/',
            json=to_post,
            headers=header
        )
        print(f"Status code: {result.status_code}")
        print(f"Result: {result.json()}")
        return result.json()

class DriverOverviewScraper(Scraper):

    def extract(self):
        drivers = self.soup.findAll('section', attrs={'class': 'card-driver'})
        parsed = {}
        for driver in drivers:
            links = driver.findAll('a')
            for link in links:
                href = link['href']
                try:
                    parsed[href]+=1
                except KeyError:
                    parsed[href] = 1
                    ds = DriverScraper(href)
                    ds.fetch()
                    ds.checkAndParse()
                    ds.extract()
                    ds._cleanData()
                    #ds.saveSoupToFile('test_driver.html')
                    self.extracted.append(ds)

if __name__ == '__main__':
    # dos = DriverOverviewScraper('drivers/pro')
    # dos.fetch()
    # dos.checkAndParse()
    # dos.extract()

    #dos.saveSoupToFile('test_driveroverview.html')

    for url in ['pro', 'prospec']:
        dos = DriverOverviewScraper('drivers/'+url)
        dos.fetch()
        dos.checkAndParse()
        dos.extract()
        for r, racer in enumerate(dos.extracted):
            result = racer.postData(pro2=url=='prospec')
            
            # new2 = {}
            # #new2['racer'] = results1[-1].json()['id']
            # new2['racer'] = r
            # new2['rank'] = racer.ranks['2019RANK']
            # new2['points'] = racer.ranks['2019Points']
            # #results2.append(requests.post('http://localhost:8000/api/addRanking/', json=new2))
            # ranking_writer.writerow([new2[x] for x in ranking_header])