# coding=utf-8
# !/usr/bin/env python3.5

import os

from imaplib import IMAP4_SSL
from smtplib import SMTP, SMTPRecipientsRefused
from email import message_from_string, message_from_file

import config


class local_connector():

    def connect(self):
        return ('OK', []) if os.path.isdir(config.TEST_DATA) else ('NO', [])

    def disconnect(self):
        pass

    def _fetch(self, selector=None, mbox=config.INPUTMAILBOX):
        dump = []
        for key, fp in enumerate(os.listdir(config.TEST_DATA)):
            path = config.TEST_DATA+"/"+fp
            dump.append((str(key), message_from_file(open(path, mode='r'))))
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


class remote_connector:

    def __init__(self):
        self.iconn = _imap_connector()
        self.sconn = _smtp_connector()

    def connect(self):
        self.sconn.connect()
        return self.iconn.connect()

    def disconnect(self):
        return self.iconn.disconnect()

    def fetch_all(self):
        return self.iconn.fetch_all()

    def fetch_unread(self):
        return self.iconn.fetch_unread()

    def move(self, id, dest_mbox):
        return self.iconn.move(id, dest_mbox)

    def cleanup(self, mbox=config.INPUTMAILBOX):
        return self.iconn.cleanup(mbox)

    def sendmail(self, msg):
        return self.sconn.sendmail(msg)


class _imap_connector:

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
            for key in [k for k in data[0].decode('utf8').split(' ') if k != '']:
                status, mail = self.socket.fetch(key, '(RFC822)')
                if status == 'OK':
                    _, body = mail[0]
                    dump[key] = message_from_string(body.decode('utf-8'))
                else:
                    raise Exception()
            return [(key, dump[key]) for key in sorted(
                        dump.keys(), key=lambda item: int(item), reverse=True)]
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

    def cleanup(self, mbox):
        self.socket.select(mbox)
        self.socket.expunge()


class _smtp_connector:

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
