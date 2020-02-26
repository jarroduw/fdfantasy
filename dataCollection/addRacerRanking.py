import csv
from drift.models import *

dic = {}
with open('racer.csv') as fi:
    reader = csv.reader(fi)
    for r, row in enumerate(reader):
        dic[row[5]] = row[6]=='pro2'

