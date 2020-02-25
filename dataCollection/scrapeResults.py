import requests
import datetime
from bs4 import BeautifulSoup
from baseScrape import Scraper

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
        winner = race.find(lambda tag: tag.name=='div' and tag.get('class') == ['driver', 'advance'])
        winner_url, winner_qRank = self._getDriverChar(winner)
        loser = race.find(lambda tag: tag.name=='div' and tag.get('class') == ['driver'])
        loser_url, loser_qRank = self._getDriverChar(loser)
        data = {
            'winner': {'url': winner_url, 'rank': winner_qRank},
            'loser':{'url': loser_url, 'rank': loser_qRank}
            }
        try:
            self.outcomes[self.round].append(data)
        except KeyError:
            self.outcomes[self.round] = [data]
        print("%s (%s) beat %s (%s)" % (winner_url, winner_qRank, loser_url, loser_qRank,))


    def _getDriverChar(self, driver):
        driverUrl = driver.find('a')['href']
        qualified = driver.find('span', attrs={'class': 'qualify'})
        qRank = qualified.text
        return driverUrl, qRank

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

def postData(extracted, scrape_datetime, pro2=False):
    with open('__sensitive_apiToken.txt') as fi:
        token = fi.read().strip()
    header = {'Authorization': 'Token %s' % (token,)}
    results_race = []
    results_q1 = []
    results_q2 = []
    for o in extracted:
        event = o.url_slug.replace('/results/', '/schedule/').replace('/pro2', '').replace('/pro', '')
        
        qDic = {'schedule_url_slug': event}
        eventObj = requests.get('http://localhost:8000/api/event/', json=qDic)
        eventId = eventObj.json()['id']
        for rd in [32, 16, 8, 4, 2]:
            try:
                outcomes = o.outcomes[rd]
                print(rd, len(outcomes))
                for race in outcomes:
                    winner = race['winner']
                    loser = race['loser']
                    ts = winner
                    bs = loser
                    if winner['rank'] > loser['rank']:
                        ts = loser
                        bs = winner
                    racer_t = requests.get(
                        'http://localhost:8000/api/racer/', json={'driver_url_slug': ts['url']}
                    ).json()['id']
                    if bs['url'] != '/drivers/bye':
                        racer_b = requests.get(
                            'http://localhost:8000/api/racer/', json={'driver_url_slug': bs['url']}
                        ).json()['id']
                    else:
                        racer_b = None
                    racer_w = requests.get(
                        'http://localhost:8000/api/racer/', json={'driver_url_slug': winner['url']}
                    ).json()['id']
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
                        'http://localhost:8000/api/race/',
                        json=raceDict_w, headers=header
                    )
                    results_race.append(result)
                    if rd == 32:
                        print("Writing qualify")
                        qualify1 = requests.post(
                            'http://localhost:8000/api/qualify/',
                            json={
                                'event': eventId,
                                'racer': racer_t,
                                'rank': ts['rank'],
                                'pro2': pro2,
                                'scraped': scrape_datetime
                            }, headers=header
                        )
                        results_q1.append(qualify1)
                        if bs['url'] != '/drivers/bye':
                            qualify2 = requests.post(
                                'http://localhost:8000/api/qualify/',
                                json={
                                    'event': eventId,
                                    'racer': racer_b,
                                    'rank': bs['rank'],
                                    'pro2': pro2,
                                    'scraped': scrape_datetime
                                }, headers=header
                            )
                            results_q2.append(qualify2)
            except KeyError:
                print("*****Missing round******:", rd)


if __name__ == '__main__':
    scrape_datetime = format(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S')
    ros_pro = ResultOverviewScraper('standings/2019/pro')
    ros_pro.fetch()
    ros_pro.checkAndParse()
    ros_pro.extract()
    postData(ros_pro.extracted, scrape_datetime)

    #ros_pro.saveSoupToFile('test_standingsoverview_pro.html')

    ros_2 = ResultOverviewScraper('standings/2019/pro2')
    ros_2.fetch()
    ros_2.checkAndParse()
    ros_2.extract()
    postData(ros_2.extracted, scrape_datetime, pro2=True)