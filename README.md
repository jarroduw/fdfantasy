# README for fdfantasy application

## Overview

Consists of a 2-part system, one for data collection and one for the actual formula drift fantasy.

## dataCollection

`dataCollection` module extracts data from `formulad.com` about racers, teams, and performance at events.

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