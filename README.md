# README for fdfantasy application

## Overview

Consists of a 2-part system, one for data collection and one for the actual formula drift fantasy.

## dataCollection

`dataCollection` module extracts data from `formulad.com` about racers, teams, and performance at events.

### Collect data

```bash
cd dataCollection
python scrapeDrivers.py
## Change code to identify the year of interest for results and then run
python scrapeResultsHistoric.py
python scrapeSchedule.py

## For continuous monitoring and scraping
python scrapeResults.py
## This one keeps running and checking for updates within a race
```

## fdfantasy

`fdfantasy` module contains the logic for the actual fdfantasy.com website.

### Initialize

```bash
sudo su - postgres
psql
> CREATE USER fdfantasy_user WITH PASSWORD '<password>';
> CREATE DATABASE fdfantasy WITH OWNER fdfantasy_user;
> \q
exit
mkdir logs
## Add your __sensitvie_dbPass.txt file at the root
python manage.py migrate
python manage.py createsuperuser
```

### Running

In addition to PostgreSQL, it also uses a redis database and huey for queue handling as it relates to drafts. To start the application, you need two separate processes. Redis can be installed using the instructions here: https://realpython.com/python-redis/

```bash
## Runs the application
python manage.py runserver

## Start Redis
redis-cli start
python manage.py run_huey

## At this point, it's all good
```