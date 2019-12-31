import requests
from bs4 import BeautifulSoup

class Scraper:
    base = "https://formulad.com/"
    removeLi = [
        'result',
        'soup'
    ]

    def __init__(self, url):
        
        self.url_slug = url
        self.url = self.base + url
        self.result = None
        self.extracted = []

    def fetch(self):
        """Retrieves web page and saves it"""

        self.result = requests.get(self.url)

    def checkAndParse(self):
        """Checks response and if 200, parses"""

        if self.result.status_code == 200:
            self.soup = BeautifulSoup(self.result.text, features='html.parser')
        else:
            raise ValueError("%s not returned" % (self.url,))

    def saveSoupToFile(self, finame):
        """Saves a soup object using prettify to finame"""

        with open(finame, 'w') as fi:
            fi.write(self.soup.prettify())

    def extract(self):
        """Extractor for data needed"""

        raise NotImplementedError("Need to implement extract function")

    def _cleanData(self):

        for r in self.removeLi:
            delattr(self, r)
