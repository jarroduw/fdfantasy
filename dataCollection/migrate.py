import requests
import csv

order = [
    'drift_event',
    'drift_racer',
    'drift_ranking',
    'drift_qualify',
    'drift_race'
    ]

eventDict = {}
with open('../drift_event.csv') as fi:
    reader = csv.reader(fi)
    for r, row in enumerate(reader):
        if r != 0:
            obj = {
                'name': row[4],
                'location': row[8],
                'schedule_url_slug': row[3],
                'address': row[5],
                'start': row[6],
                'end': row[7]
            }
            result = requests.post('http://fdfantasy.com/api/event/', json=obj)
            eventDict[row[0]] = result.json()['id']

rankingDict = {}
with open('../drift_ranking.csv') as fi:
    reader = csv.reader(fi)
    for r, row in enumerate(reader):
        if r != 0:
            try:
                temp = rankingDict[row[4]]
                print("ERROR WITH DUPLICATE IDs")
            except KeyError:
                rankingDict[row[4]] = row


racerDict = {}
with open('../drift_racer.csv') as fi:
    reader = csv.reader(fi)
    for r, row, in enumerate(reader):
        if r != 0:
            rankingData = rankingDict[row[0]]
            obj = {
                'driver_url_slug': row[4],
                'team_name': row[7],
                'name': row[3],
                'car_number': row[5],
                'car_manuf': row[6],
            }
            rankObj = {
                'racer': None,
                'rank': rankingData[3],
                'points': rankingData[4]
            }
            result1 = requests.post('http://fdfantasy.com/api/racer/', json=obj)
            print("Posted racer")
            if result1.status_code == 201:
                print("posting rank")
                racerDict[row[0]] = result1.json()['id']
                rankObj['racer'] = result1.json()['id']
                result2 = requests.post('http://fdfantasy.com/api/ranking/', json=rankObj)
            else:
                raise AttributeError("NO RESULT")

with open('../drift_qualify.csv') as fi:
    reader = csv.reader(fi)
    for r, row in enumerate(reader):
        if r != 0:
            driver = racerDict[row[5]]
            event = eventDict[row[4]]
            obj = {
                'event': event,
                'racer': driver,
                'rank': row[3]
            }
            requests.post('http://fdfantasy.com/api/qualify/', json=obj)

with open('../drift_race.csv') as fi:
    reader = csv.reader(fi)
    for r, row in enumerate(reader):
        if r != 0:
            try:
                bottom = racerDict[row[3]]
            except KeyError:
                bottom = None
            top = racerDict[row[5]]
            winner = racerDict[row[7]]
            event = eventDict[row[4]]
            rd = row[6]
            obj = {
                'top_seed': top,
                'bottom_seed': bottom,
                'winner': winner,
                'event': event,
                'event_round': rd
            }
            result = requests.post('http://fdfantasy.com/api/race/', json=obj)
