# Charon
Lightweight adaptable Mailparser

## Requirements
* [Python3.4](https://www.python.org/download/releases/3.4.0/)
* [PIP3](https://pypi.python.org/pypi/pip)

## Installation
1. Run `$ pip3 install charon-x.x.x.tar.gz`
2. Create a config file (`.charon.cfg`) with `$ charon --crconf` which is placed in the home dir of the current user.

**Important** At the moment the IMAP connection has to be IMAPv4 SSL and SMTP starttls
## Usage
The queried Mail-Account has to have a `matched` and `unmatched` folder in which the handled mails are placed accordingly.

The Footer used in the Mailresponse can be placed in any text-file and then configured in the config-file.

The Handler has to be triggered with `$ charon`, for example by cron.  
To prevent bugs the complete path should be referenced in the crontab, `$ which charon` shows it.