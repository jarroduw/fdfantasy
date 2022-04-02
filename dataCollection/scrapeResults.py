import requests
import datetime
import time
import logging
from scrapeResultsHistoric import ResultScraper

log_format = '%(levelname)s %(asctime)s %(module)s %(message)s'
logging.basicConfig(filename='event_scraper_service.log', level=logging.DEBUG, format=log_format)
#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    
    event_active = False
    time_to_next_event = 0
    while True:
        logger.info("Service running and functioning")
        result = requests.get('http://localhost:8000/api/event/', json={'get_latest': True})
        if result.status_code == 200:
            data = result.json()
            logger.debug("Data from event: %s", data)
            scrapetime = datetime.datetime.utcnow()
            if data['start'] is not None:
                starttime = datetime.datetime.strptime(data['start'], "%Y-%m-%d")
            if data['start'] is not None and starttime <= scrapetime:
                logger.debug("Collecting results")
                ## Get result url
                ## Scrape event result
                ## postData
                result_url_base = data['schedule_url_slug'].replace('schedule', 'results')
                prospec_result_url = f"{result_url_base}/prospec"
                pro_result_url = f"{result_url_base}/pro"
                rs = ResultScraper(pro_result_url)
                rs.fetch()
                rs.checkAndParse()
                rs.extract()
                rs.postData(format(scrapetime, '%Y-%m-%d %H:%M:%S'), False)

        ## If changes, parse out events and write to database
        logger.info("Finished event check-in, going to sleep")
        ## Sleep for 15 minutes, or until the next check-in period
        time.sleep(15*60)