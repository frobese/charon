# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8
# !/usr/bin/env python3.5

from absencehandler.connector import remote_connector, local_connector
from absencehandler.matched import matched

from datetime import datetime

import argparse
import os
import logging
import sys


def prod(connector, conf):
    if not 'INBOX' == conf.INPUTMAILBOX:
        logging.error("HANDLER - {} not a valid prod mailbox".format(conf.INPUTMAILBOX))
        return 0

    messages = connector.fetch_unawnsered()
    logging.info('HANLDER - {} fetched'.format(len(messages)))
    for ID, msg in messages:
        logging.info('HANLDER - reached <{}>'.format(msg['subject']))
        match_obj = matched(msg)
        if match_obj.is_matched:
            logging.info('HANDLER - message {} matched'.format(ID))
            msg = match_obj.msg_response()
            msg['from'] = conf.ORIGIN
            msg['to'] = match_obj.recipient
            msg.add_header('bcc', ", ".join(conf.REPORT_RECIPIENTS))
            msg.add_header('reply-to', conf.REPLY_TO)
            logging.debug('HANDLER - response composed')
            if not connector.sendmail(msg):
                logging.critical(
                    'HANDLER - <{}> could not be send'.format(msg['subject']))
                break
            else:
                connector.flag_awnsered(ID)
        else:
            logging.info('HANDLER - message {} unmatched'.format(ID))

        if conf.REPORT_RECIPIENTS:
            logging.info('HANDLER - composing report for {}'.format(ID))
            report_msg = match_obj.msg_response(report=True)
            report_msg['from'] = conf.ORIGIN
            report_msg['to'] = ", ".join(conf.REPORT_RECIPIENTS)
            logging.debug('HANDLER - report composed')
            if connector.sendmail(report_msg):
                if match_obj.is_matched:
                    connector.copy(ID, 'matched')
                else:
                    connector.flag_awnsered(ID)
                    connector.copy(ID, 'unmatched')
            else:
                logging.error(
                    'HANDLER - <{}> could not be send'.format(report_msg['subject']))
        else:
            logging.error(
                    'HANDLER - no report recipients were configured')
    logging.info('HANDLER - done.')
    # connector.cleanup()


def debug(connector, conf, step, diff):
    messages = connector.fetch_all()
    logging.info('HANLDER - {} fetched'.format(len(messages)))
    for ID, msg in messages:
        match_obj = matched(msg)
        if (diff and (match_obj.is_matched) == (conf.INPUTMAILBOX == 'matched')) or not diff:
            print("MAILBOX: {}".format(conf.INPUTMAILBOX))
            print(match_obj.debug_output())
            if step:
                inp = input()
                if (inp == 'move' and not (
                        (conf.INPUTMAILBOX == 'matched') == match_obj.is_matched)):
                    if match_obj.is_matched:
                        connector.move(ID, 'matched')
                    else:
                        connector.move(ID, 'unmatched')
                elif inp == 'move':
                    print("MOVE FROM: {} TO {} NOT VALID".format(
                        conf.INPUTMAILBOX,
                        'matched' if match_obj.is_matched else 'unmatched'))
                    input()
                elif inp == 'abort':
                    break
            os.system('clear')
    # connector.cleanup()
