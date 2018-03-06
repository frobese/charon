# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8

from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG
from configparser import ConfigParser
import os
import logging

class config:

    _footer = None

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
            'FOOTER_PATH' : "None",
            'KEEP_ATTACHMENT' : False,
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
            'LOCATION' : '/var/log'
        }

        configfile = open(os.path.expanduser('~/.charon.cfg'), 'w')
        self._conf.write(configfile)

    def read_config(self):
        if not self._conf.read(os.path.expanduser('~/.charon.cfg')):
            raise IOError

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
        if not self._footer:
            ffp = self._conf.get('GENERAL','FOOTER_PATH')

            if ffp and ffp != "None":
                try:
                    logging.info('HANDLER - Fetching footerfile')
                    footer_file = open(ffp, 'r')
                    self._footer = "".join(footer_file.readlines())
                except(IOError):
                    logging.critical('HANDLER - Footerfile could not be opened')
                    return 0
            else:
                self._footer = ""

        return self._footer
            

    @property
    def KEEP_ATTACHMENT(self):
        return self._conf.getboolean('GENERAL','KEEP_ATTACHMENT')

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