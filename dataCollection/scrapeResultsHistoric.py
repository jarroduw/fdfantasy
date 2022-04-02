import requests
import datetime
from bs4 import BeautifulSoup
from baseScrape import Scraper
from scrapeDrivers import DriverScraper
from scrapeSchedule import EventScraper

class ResultScraper(Scraper):

    def extract(self):
        eventName = self.soup.find('h1', attrs={'class': 'result-title'})
        print(eventName.text)
        self.event = eventName.text
        self.outcomes = {}
        results = self.soup.findAll('div', attrs={'class': 'result-panel'})
        for result in results:
            self._getBracketRound(result['id'])
            racesUL = result.findAll('ul', attrs={'class': 'list-results'})
            for raceLi in racesUL:
                races = raceLi.findAll('li')
                raceCount = 0
                for race in races:
                    self._parseRace(race)
                    raceCount += 1

    def _getBracketRound(self, rd):
        rd = rd.replace("resultPanel", "")
        print("ROUND", rd)
        rd = int(rd)
        self.round = rd

    def _parseRace(self, race):
        """Takes a given race, and first looks for a driver that advances. Then looks for all drivers and
        assumes that the one that's not the winner is the loser. If no winner, then it blows stuff up."""

        ##TODO: Re-structure so it finds both drivers and gets characteristics, returns winner position in list

        ## Start by getting driver pairs
        all_drivers = race.find_all("div", {'class': 'driver'})
        new_data_drivers = []
        for driver in all_drivers:
            new_data_drivers.append(self._getDriverChar(driver))
        print("=========================")
        print(new_data_drivers)
        print("=========================")

        new_data_drivers.sort(key=lambda x: x['rank'])

        ##TODO: Change structure so it returns top seed and bottom seed and includes a true/false for winner
        data = {
            'top_seed': new_data_drivers[0],
            'bottom_seed': new_data_drivers[1]
            }
        try:
            self.outcomes[self.round].append(data)
        except KeyError:
            self.outcomes[self.round] = [data]
        print(
            "%s (%s: winner=%s) top seed over %s (%s: winner=%s)" % (
                data['top_seed']['url'],
                data['top_seed']['rank'],
                data['top_seed']['winner'],
                data['bottom_seed']['url'],
                data['bottom_seed']['rank'],
                data['bottom_seed']['winner'],
                )
            )

    def _getDriverChar(self, driver):
        driverUrl = driver.find('a')['href']
        qualified = driver.find('span', attrs={'class': 'qualify'})
        qRank = qualified.text
        if qRank is not None and qRank.lower() != 'x':
            qRank = int(qRank)
        else:
            qRank = 99
        winner_found = driver.find(lambda tag: tag.name=='div' and tag.get('class') == ['driver', 'advance'])
        winner = True
        if winner_found is None:
            winner = False
        return {'url': driverUrl, 'rank': qRank, 'winner': winner}

    def postData(self, scrape_datetime, pro2=False, base='http://localhost:8000/', tokenPath='__sensitive_apiToken.txt'):
        with open(tokenPath) as fi:
            token = fi.read().strip()
        header = {'Authorization': 'Token %s' % (token,)}
        event = self.url_slug.replace('/results/', '/schedule/').replace('/prospec', '').replace('/pro', '')
        print(event)
        
        qDic = {'schedule_url_slug': event}
        eventObj = requests.get(base + 'api/event/', json=qDic)
        try:
            eventId = eventObj.json()['id']
        except KeyError:
            es = EventScraper(event)
            es.fetch()
            es.checkAndParse()
            es.extract()
            result = requests.post(
                base + 'api/event/',
                headers=header,
                json={
                    'name': es.name,
                    'location': es.location,
                    'schedule_url_slug': es.url_slug,
                    'address': es.addr,
                    'start': format(es.startDate, '%Y-%m-%d'),
                    'end': format(es.endDate, '%Y-%m-%d')
                }
            )
            if result.status_code != 201:
                print("ERROR", result.json())
            eventId = result.json()['id']
        for rd in [32, 16, 8, 4, 2]:
            try:
                outcomes = self.outcomes[rd]
                for race in outcomes:
                    ts = race['top_seed']
                    bs = race['bottom_seed']
                    if ts['url'] != '#' and bs['url'] != '#':
                        ## Assume that if both records are blank, there's nothing

                        ###########################################
                        ## FIRST WE HANDLE FINDING DRIVER RECORDS

                        ## IF NO DRIVER RECORD, GO GET IT
                        if ts['url'] not in ['/drivers/bye', 'racer/bye', '#']:
                            if ts['url'] == '/drivers/benhobson':
                                ts['url'] = '/drivers/ben-hobson'
                            if ts['url'] == '/drivers/hoomanrahimi':
                                ts['url'] = '/drivers/hooman-rahimi'
                            try:
                                racer_t = requests.get(
                                    base + 'api/racer/', json={'driver_url_slug': ts['url']}
                                ).json()[0]['id']
                            except IndexError:
                                print("No ts driver record, need to handle!")
                                ds = DriverScraper(ts['url'])
                                ds.fetch()
                                ds.checkAndParse()
                                ds.extract()
                                ds._cleanData()
                                print(ds.__dict__)
                                racer_t = ds.postData(base=base, pro2=pro2, tokenPath=tokenPath)[0]['id']
                        if bs['url'] not in ['/drivers/bye', 'racer/bye', '#']:
                            if bs['url'] == '/drivers/benhobson':
                                bs['url'] = '/drivers/ben-hobson'
                            if bs['url'] == '/drivers/hoomanrahimi':
                                bs['url'] = '/drivers/hooman-rahimi'
                            try:
                                racer_b = requests.get(
                                    base + 'api/racer/', json={'driver_url_slug': bs['url']}
                                ).json()
                                print(racer_b, bs['url'])
                                racer_b = racer_b[0]['id']
                            except IndexError:
                                print("No bs driver record, need to handle!")
                                ds = DriverScraper(bs['url'])
                                ds.fetch()
                                ds.checkAndParse()
                                ds.extract()
                                ds._cleanData()
                                print(ds.__dict__)
                                racer_b = ds.postData(base=base, pro2=pro2, tokenPath=tokenPath)[0]['id']
                        else:
                            racer_b = None

                        #############################################
                        ## NOW WE CHECK FOR A WINNER
                        ## Check if there's a winner
                        if not bs['winner'] and not ts['winner']:
                            racer_w = None
                        else:
                            ## If there is, assume it's top seed
                            racer_w = racer_t
                            if bs['winner']:
                                ## But if it's bottom seed, set that
                                racer_w = racer_b
                        raceDict_w = {
                            'event': eventId,
                            'top_seed': racer_t,
                            'bottom_seed': racer_b,
                            'winner': racer_w,
                            'event_round': rd,
                            'pro2': pro2,
                            'scraped': scrape_datetime
                        }
                        if pro2 and rd == 32:
                            raceDict_w['event_round'] = 16
                        result = requests.post(
                            base + 'api/race/',
                            json=raceDict_w,
                            headers=header
                        )
                        if rd == 32 or (pro2 and rd == 16):
                            qualify1 = requests.post(
                                base + 'api/qualify/',
                                json={
                                    'event': eventId,
                                    'racer': racer_t,
                                    'rank': ts['rank'],
                                    'pro2': pro2,
                                    'scraped': scrape_datetime
                                }, headers=header
                            )
                            if bs['url'] != '/drivers/bye':
                                qualify2 = requests.post(
                                    base + 'api/qualify/',
                                    json={
                                        'event': eventId,
                                        'racer': racer_b,
                                        'rank': bs['rank'],
                                        'pro2': pro2,
                                        'scraped': scrape_datetime
                                    }, headers=header
                                )
            except KeyError:
                print("*****Missing round******:", rd)

class ResultOverviewScraper(Scraper):

    def extract(self):
        brackets = self.soup.findAll("li", attrs={'class': 'bracket'})
        for bracket in brackets:
            link = bracket.findAll('a')[0]
            actualLink = link['href']
            rs = ResultScraper(actualLink)
            rs.fetch()
            rs.checkAndParse()

            #rs.saveSoupToFile('test_standing.html')
            rs.extract()
            rs._cleanData()
            self.extracted.append(rs)

def postData(extracted, scrape_datetime, pro2=False, base='http://localhost:8000/', tokenPath='__sensitive_apiToken.txt'):
    with open(tokenPath) as fi:
        token = fi.read().strip()
    header = {'Authorization': 'Token %s' % (token,)}
    for o in extracted:
        o.postData(scrape_datetime, pro2=pro2, base=base, tokenPath=tokenPath)

if __name__ == '__main__':
    scrape_datetime = format(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S')
    ros_pro = ResultOverviewScraper('standings/2021/pro')
    ros_pro.fetch()
    ros_pro.checkAndParse()
    ros_pro.extract()
    postData(ros_pro.extracted, scrape_datetime)

    #ros_pro.saveSoupToFile('test_standingsoverview_pro.html')

    # ros_2 = ResultOverviewScraper('standings/2018/pro2')
    # ros_2.fetch()
    # ros_2.checkAndParse()
    # ros_2.extract()
    # postData(ros_2.extracted, scrape_datetime, pro2=True)