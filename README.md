# Absence Handler
Lightweight adaptable Mailparser

## Requirements
* [Python3](https://www.python.org/download/releases/3.0/)

## Installation
1. Run `$ pip3 install AbsenceHandler-x.x.x.tar.gz`
2. Create a default config file with `$ absencehandler --crconf` which is placed in the home dir of the current user.

The Handler has to be triggered with `$ absencehandler`, for example by cron.  
To prevent bugs the complete path should be referenced in the crontab, `$ which absencehandler` shows it.
## Licence
    Copyright (C) frobese GmbH - All Rights Reserved
    Unauthorized copying, via any medium is strictly prohibited
    Proprietary and confidential
    Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017