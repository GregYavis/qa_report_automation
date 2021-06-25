#!/bin/bash
python manage.py crontab add
python manage.py crontab run 6d032af6cd069212a1d8951f854b006b
python manage.py crontab remove