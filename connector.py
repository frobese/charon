# coding=utf-8
# !/usr/bin/env python3.5

import os

from imaplib import IMAP4_SSL
from smtplib import SMTP, SMTPRecipientsRefused
from email import message_from_string, message_from_file

import config


class imap_connector:

    def connect(self):
        self.socket = IMAP4_SSL(host=config.HOST, port=config.IMAP_PORT)
        return self.socket.login(config.USERNAME, config.PASSWORD)

    def disconnect(self):
        return self.socket.logout()

    def _fetch(self, selector, mbox=config.INPUTMAILBOX):
        self.socket.select(mbox)
        status, data = self.socket.search(None, selector)
        if status == 'OK':
            dump = {}
            for key in data[0].decode('utf8').split(' '):
                status, mail = self.socket.fetch(key, '(RFC822)')
                if status == 'OK':
                    _, body = mail[0]
                    dump[key] = message_from_string(body.decode('utf-8'))
                else:
                    raise Exception()
            return dump
        else:
            raise Exception()

    def fetch_all(self):
        return self._fetch('ALL UNDELETED')

    def fetch_unread(self):
        return self._fetch('UNSEEN UNDELETED')

    def move(self, id, dest_mbox):
        if not dest_mbox == config.INPUTMAILBOX:
            status, _ = self.socket.copy(id, dest_mbox)
            if status == 'OK':
                self.socket.store(id, '+FLAGS', '\\Deleted')

    def cleanup(self, mbox=config.INPUTMAILBOX):
        self.socket.select(mbox)
        self.socket.expunge()


class smtp_connector:

    def connect(self):
        self.socket = SMTP(host=config.HOST, port=config.SMTP_PORT)
        self.socket.starttls()
        self.socket.login(config.USERNAME, config.PASSWORD)

    def sendmail(self, msg):
        try:
            self.socket.send_message(msg)
            return True
        except(SMTPRecipientsRefused):
            return False


class local_connector(imap_connector):

    def connect(self):
        return ('OK', []) if os.path.isdir(config.TEST_DATA) else ('NO', [])

    def disconnect(self):
        pass

    def _fetch(self, selector=None, mbox=config.INPUTMAILBOX):
        dump = {}
        for key, fp in enumerate(os.listdir(config.TEST_DATA)):
            path = config.TEST_DATA+"/"+fp
            dump[str(key)] = message_from_file(open(path, mode='r'))
        return dump

    def fetch_all(self):
        return self._fetch()

    def fetch_unread(self):
        return self._fetch()

    def move(self, id, dest_mbox):
        pass

    def cleanup(self, mbox=config.INPUTMAILBOX):
        pass

    def sendmail(self, msg):
        print(msg)
