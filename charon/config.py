# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8

from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG
from configparser import ConfigParser
import os

class config:

    def __init__(self, write_conf=False):
        self._conf = ConfigParser()
        if not write_conf:
            self.read_config()
        else:
            self.ceate_dafault_conf()

    def ceate_dafault_conf(self):
        self._conf['GENERAL'] = {
            'REPORT_RECIPIENTS' : 'john.doe@example.com, jane.doe@example.com',
            'ORIGIN' : 'noreply@example.com',
            'REPLY_TO' : 'james.doe@example.com',
            'FOOTER_PATH' : None
        }
        self._conf['MAIL'] = {
            'HOST': 'www.example.com',
            'IMAP_PORT' : 993,
            'SMTP_PORT' : 587,
            'USERNAME' : 'jdoe',
            'PASSWORD' : 'secret123',
            'INPUTMAILBOX' : 'INBOX'
        }
        self._conf['LOG'] = {
            'LEVEL' : 'INFO',
            'LOCATION' : '/tmp'
        }

        configfile = open(os.path.expanduser('~/.charon.cfg'), 'w')
        self._conf.write(configfile)

    def read_config(self):
        self._conf.read(os.path.expanduser('~/.charon.cfg'))

    @property
    def REPORT_RECIPIENTS(self):
        return self._conf.get('GENERAL','REPORT_RECIPIENTS').replace(' ','').split(',')

    @property
    def ORIGIN(self):
        return self._conf.get('GENERAL','ORIGIN')

    @property
    def REPLY_TO(self):
        return self._conf.get('GENERAL','REPLY_TO')  

    @property
    def FOOTER(self):
        ffp = self._conf.get('GENERAL','FOOTER_PATH')
        return ffp if ffp and ffp != "None" else None

    @property
    def HOST(self):
        return self._conf.get('MAIL','HOST')

    @property
    def IMAP_PORT(self):
        return self._conf.get('MAIL','IMAP_PORT')  

    @property
    def SMTP_PORT(self):
        return self._conf.get('MAIL','SMTP_PORT')

    @property
    def USERNAME(self):
        return self._conf.get('MAIL','USERNAME')  

    @property
    def PASSWORD(self):
        return self._conf.get('MAIL','PASSWORD')

    @property
    def INPUTMAILBOX(self):
        return self._conf.get('MAIL','INPUTMAILBOX')  

    @property
    def LEVEL(self):
        return self._conf.get('LOG','LEVEL')

    @property
    def LOCATION(self):
        return self._conf.get('LOG','LOCATION')