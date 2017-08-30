# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8
# !/usr/bin/env python3.5

import os
import logging

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
            path = config.TEST_DATA+'/'+fp
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

    def fetch_unawnsered(self):
        return self.iconn.fetch_unawnsered()

    def move(self, id, dest_mbox):
        return self.iconn.move(id, dest_mbox)

    def copy(self, id, dest_mbox):
        return self.iconn.copy(id, dest_mbox)

    def cleanup(self, mbox=config.INPUTMAILBOX):
        return self.iconn.cleanup(mbox)

    def sendmail(self, msg):
        return self.sconn.sendmail(msg)

    def flag_deleted(self, id):
        return self.iconn.flag_deleted(id)

    def flag_seen(self, id):
        return self.iconn.flag_seen(id)

    def flag_awnsered(self, id):
        return self.iconn.flag_awnsered(id)


class _imap_connector:

    def connect(self):
        logging.info('IMAP - establishing connection')
        self.socket = IMAP4_SSL(host=config.HOST, port=config.IMAP_PORT)
        (state, _) = self.socket.login(config.USERNAME, config.PASSWORD)
        if(state == 'OK'):
            logging.debug('IMAP - connection successful')
        else:
            logging.error('IMAP - connection failed')

    def disconnect(self):
        logging.info('IMAP - disconnect')
        return self.socket.logout()

    def _fetch(self, selector, mbox=config.INPUTMAILBOX):
        self.socket.select(mbox)
        logging.info('IMAP - probing {}'.format(mbox))
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
                    dump[key] = message_from_string(body.decode('utf-8'))
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
        if not dest_mbox == config.INPUTMAILBOX:
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
        logging.info('IMAP - expunging {}'.format(mbox))
        self.socket.select(mbox)
        self.socket.expunge()


class _smtp_connector:

    def connect(self):
        logging.info('SMTP - establishing connection')
        self.socket = SMTP(host=config.HOST, port=config.SMTP_PORT)
        self.socket.starttls()
        code, msg = self.socket.login(config.USERNAME, config.PASSWORD)
        logging.debug('SMTP - connection responce is {}: {}'.format(code, msg))

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
        except(SMTPNotSupportedError):
            logging.critical('SMTP - not supportet error')
            return False
