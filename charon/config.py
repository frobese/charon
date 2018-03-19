# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8

from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG
from configparser import ConfigParser, Error
import os
import logging

class config:

    _footer = None

    def __init__(self):
        self._conf = ConfigParser()

    def ceate_dafault_conf(self):
        self.init_dafault_conf()
        self.write_config()


    def init_dafault_conf(self):
        self._conf['GENERAL'] = {
            'REPORT_RECIPIENTS' : 'john.doe@example.com, jane.doe@example.com',
            'ORIGIN' : 'noreply@example.com',
            'REPLY_TO' : 'james.doe@example.com',
            'FOOTER_PATH' : "~/charon_signature.txt",
            'KEEP_ATTACHMENT' : True,
        }
        self._conf['MAIL'] = {
            'HOST': 'www.example.com',
            'IMAP_PORT' : 993,
            'SMTP_PORT' : 587,
            'USERNAME' : 'jdoe',
            'PASSWORD' : 'secret123',
            'INPUTMAILBOX' : 'planung',
            'POSITIVE_BOX': 'erledigt',
            'NEGATIVE_BOX': 'todo'
        }
        self._conf['LOG'] = {
            'LEVEL' : 'INFO',
            'LOCATION' : '/var/log'
        }

    def update_config(self, verbose = False):
        if verbose:
            print("Init defaults ...")
        self.init_dafault_conf()
        if verbose:
            print("Read Config ...")
        self.read_config()
        if verbose:
            print("Write updated config ...")
        self.write_config()

    def write_config(self):
        configfile = open(os.path.expanduser('~/charon.cfg'), 'w')
        self._conf.write(configfile)

    def read_config(self):
        if not self._conf.read(os.path.expanduser('~/charon.cfg')):
            raise IOError
        if not self.self_check():
            raise Error('Config is incomplete')

    def self_check(self):
        default = config()
        default.init_dafault_conf()

        for sect in default._conf.sections():
            if not self._conf.has_section(sect):
                return False

            for opt in default._conf.options(sect):
                if not self._conf.has_option(sect, opt):
                    return False
        return True

    @property
    def REPORT_RECIPIENTS(self):
        return [
            rec for rec in 
            self._conf.get(
                'GENERAL','REPORT_RECIPIENTS'
            ).replace(' ','').split(',') 
            if rec is not ''
        ]

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
            ffp = os.path.expanduser(ffp) if '~' in ffp else ffp

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
    def POSITIVE_BOX(self):
        return self._conf.get('MAIL', 'POSITIVE_BOX')
    @property
    def NEGATIVE_BOX(self):
        return self._conf.get('MAIL', 'NEGATIVE_BOX')

    @property
    def LIST_BOXES(self):
        return [self.INPUTMAILBOX, self.POSITIVE_BOX, self.NEGATIVE_BOX]

    @property
    def LEVEL(self):
        return self._conf.get('LOG','LEVEL')

    @property
    def LOCATION(self):
        return self._conf.get('LOG','LOCATION')