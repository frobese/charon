# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8
# !/usr/bin/env python3.5

import os
import logging

from imaplib import IMAP4_SSL
from smtplib import (SMTP, SMTPRecipientsRefused, SMTPHeloError,
                     SMTPSenderRefused, SMTPDataError, SMTPAuthenticationError)
from email import message_from_bytes, message_from_file

class local_connector:

    def __init__(self, conf, path):
        self._conf = conf
        if '~' in path:
            self._path = os.path.expanduser(path)
        else:
            self._path = path

    def connect(self):
        return ('OK', []) if os.path.isdir(self._path) else ('NO', [])

    def disconnect(self):
        pass

    def _fetch(self, selector=None):
        dump = []
        for key, fp in enumerate(os.listdir(self._path)):
            path = self._path + '/' + fp
            dump.append((str(key), message_from_file(open(path, mode='r'))))
        return dump

    def fetch_all(self):
        return self._fetch()

    def fetch_unread(self):
        return self._fetch()

    def fetch_unawnsered(self):
        return self._fetch()

    def move(self, id, dest_mbox):
        pass

    def copy(self, id, dest_mbox):
        pass

    def cleanup(self):
        pass

    def sendmail(self, msg):
        print(msg)
        return True

    def flag_deleted(self, id):
        pass

    def flag_seen(self, id):
        pass

    def flag_awnsered(self, id):
        pass


class remote_connector:

    def __init__(self, conf):
        self._conf = conf

        self.iconn = _imap_connector(self._conf)
        self.sconn = _smtp_connector(self._conf)

    def connect(self):
        return (self.iconn.connect() and self.sconn.connect())

    def disconnect(self):
        return self.iconn.disconnect()

    def init_mboxes(self):
        return self.iconn.init_mboxes()

    def fetch_all(self):
        return self.iconn.fetch_all()

    def fetch_unread(self):
        return self.iconn.fetch_unread()

    def fetch_unawnsered(self):
        return self.iconn.fetch_unawnsered()

    def move(self, id, dest_mbox):
        return self.iconn.move(id, dest_mbox)

    def copy(self, id, dest_mbox):
        return self.iconn.copy(id, dest_mbox)

    def cleanup(self):
        return self.iconn.cleanup(self._conf.INPUTMAILBOX)

    def sendmail(self, msg):
        return self.sconn.sendmail(msg)

    def flag_deleted(self, id):
        return self.iconn.flag_deleted(id)

    def flag_seen(self, id):
        return self.iconn.flag_seen(id)

    def flag_awnsered(self, id):
        return self.iconn.flag_awnsered(id)


class _imap_connector:

    def __init__(self, conf):
       self._conf = conf

    def connect(self):
        logging.info('IMAP - establishing connection')
        self.socket = IMAP4_SSL(host=self._conf.HOST, port=self._conf.IMAP_PORT)
        try:
            (state, _) = self.socket.login(self._conf.USERNAME, self._conf.PASSWORD)
            logging.debug('IMAP - connection successful')
            return True
        except:
            logging.error('IMAP - connection failed')
        return False
    def disconnect(self):
        logging.info('IMAP - disconnect')
        return self.socket.logout()

    def init_mboxes(self):
        logging.info('IMAP - create missing mailboxes')
        boxes = []
        try:
            current_boxes = [
                bx.decode('utf-8').split(' "." ')[-1] 
                    for bx in self.socket.list()[1]
            ]
            
            boxes = [mbox for mbox in self._conf.LIST_BOXES if mbox not in current_boxes]
        except:
            logging.error('IMAP - failed to list mailboxes')

        for mbox in boxes:
            try:
                self.socket.create(mbox)
                logging.info('IMAP - created mailbox {}'.format(mbox))
            except PermissionError:
                logging.error('IMAP - failed to create mailbox {}'.format(mbox))


    def _fetch(self, selector):
        self.socket.select(self._conf.INPUTMAILBOX)
        logging.info('IMAP - probing {}'.format(self._conf.INPUTMAILBOX))
        status, data = self.socket.search(None, selector)
        if status == 'OK':
            logging.debug('IMAP - probe successful')
            dump = {}
            for key in [k for k in data[0].decode('utf8').split(' ') if k != '']:
                logging.debug('IMAP - fetching mail {}'.format(key))
                status, mail = self.socket.fetch(key, '(RFC822)')
                if status == 'OK':
                    logging.debug('IMAP - fetching mail successful')
                    _, body = mail[0]
                    dump[key] = message_from_bytes(body)
                else:
                    logging.critical('IMAP - mail {} could not be fetched'.format(key))
                    raise Exception()
            return [(key, dump[key]) for key in sorted(
                        dump.keys(), key=lambda item: int(item), reverse=True)]
        else:
            logging.critical('IMAP - probe unsuccessful')
            raise Exception()

    def fetch_all(self):
        logging.info('IMAP - fetching undeleted')
        return self._fetch('UNDELETED')

    def fetch_unread(self):
        logging.info('IMAP - fetching unread and undeleted')
        return self._fetch('UNSEEN UNDELETED')

    def fetch_unawnsered(self):
        logging.info('IMAP - fetching unanswered and undeleted')
        return self._fetch('UNANSWERED UNDELETED')

    def move(self, id, dest_mbox):
        logging.info('IMAP - moving {} to {}'.format(id, dest_mbox))
        if self.copy(id, dest_mbox):
            self.flag_deleted(id)
        else:
            logging.error('IMAP - move aborted')

    def copy(self, id, dest_mbox):
        if not dest_mbox == self._conf.INPUTMAILBOX:
            logging.info('IMAP - copy {} to {}'.format(id, dest_mbox))
            status, _ = self.socket.copy(id, dest_mbox)
            if status == 'OK':
                logging.debug('IMAP - copy successful')
                return True
            else:
                logging.error('IMAP - copy unsuccessful')
                return False

    def flag_deleted(self, id):
        logging.info('IMAP - flagging {} deleted'.format(id))
        self.socket.store(id, '+FLAGS', '\\Deleted')

    def flag_seen(self, id):
        logging.info('IMAP - flagging {} seen'.format(id))
        self.socket.store(id, '+FLAGS', '\\Seen')

    def flag_awnsered(self, id):
        logging.info('IMAP - flagging {} awnsered'.format(id))
        self.socket.store(id, '+FLAGS', '\\Answered')

    def cleanup(self, mbox):
        logging.warning('IMAP - expunging {}'.format(mbox))
        self.socket.select(mbox)
        self.socket.expunge()


class _smtp_connector:

    def __init__(self, conf):
       self._conf = conf

    def connect(self):
        logging.debug('SMTP - establishing connection')
        self.socket = SMTP(host=self._conf.HOST, port=self._conf.SMTP_PORT)
        self.socket.starttls()
        try:
            code, msg = self.socket.login(self._conf.USERNAME, self._conf.PASSWORD)
            logging.info('SMTP - connection successful')
            return True
        except SMTPAuthenticationError:
            logging.info('SMTP - connection failed')
        return False

    def sendmail(self, msg):
        try:
            self.socket.send_message(msg)
            logging.info('STMP - send successful')
            return True
        except(SMTPRecipientsRefused):
            logging.critical('STMP - recipients refused')
            return False
        except(SMTPHeloError):
            logging.critical('SMTP - helo error')
            return False
        except(SMTPSenderRefused):
            logging.critical('SMTP - sender refused')
            return False
        except(SMTPDataError):
            logging.critical('SMTP - data error')
            return False
