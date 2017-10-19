# Absence Handler
Lightweight adaptable Mailparser

## Requirements
* [Python3.4](https://www.python.org/download/releases/3.4.0/)
* [PIP3](https://pypi.python.org/pypi/pip)

## Installation
1. Run `$ pip3 install AbsenceHandler-x.x.x.tar.gz`
2. Create a default config file with `$ absencehandler --crconf` which is placed in the home dir of the current user.

## Usage
The queried Mail-Account has to have a `matched` and `unmatched` folder in which the handled mails are placed accordingly.

The Handler has to be triggered with `$ absencehandler`, for example by cron.  
To prevent bugs the complete path should be referenced in the crontab, `$ which absencehandler` shows it.