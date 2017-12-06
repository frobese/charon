# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8
# !/usr/bin/env python3.5

try:
    from charon.connector import remote_connector, local_connector
    from charon.matched import matched
except ImportError:
    from connector import remote_connector, local_connector
    from matched import matched

from datetime import datetime

import argparse
import os
import logging
import sys


def prod(connector, conf):
    if not 'INBOX' == conf.INPUTMAILBOX:
        logging.error("HANDLER - {} not a valid prod mailbox".format(conf.INPUTMAILBOX))
        return 0

    if conf.FOOTER:
        try:
            logging.info('HANDLER - Fetching footerfile')
            footer_file = open(conf.FOOTER, 'r')
            footer = "\n".join(footer_file.readlines())
        except(IOError):
            logging.critical('HANDLER - Footerfile could not be opened')
            return 0
    else:
        footer = ""

    messages = connector.fetch_unawnsered()
    logging.info('HANDLER - {} fetched'.format(len(messages)))
    for ID, msg in messages:
        logging.info('HANDLER - reached {} <{}>'.format(ID, msg['subject']))
        match_obj = matched(msg, conf.KEEP_ATTACHMENT, footer=footer)
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
                    'HANDLER - error while sending {}'.format(ID))
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
                    connector.move(ID, 'matched')
                else:
                    connector.flag_awnsered(ID)
                    connector.move(ID, 'unmatched')
            else:
                logging.error(
                    'HANDLER - error while sending {}'.format(ID))
        else:
            logging.error(
                    'HANDLER - no report recipients were configured')
    logging.debug('HANDLER - done.')
    connector.cleanup()


def debug(connector, conf, step, diff):
    messages = connector.fetch_all()

    logging.warning('HANDLER - Running in debug mode')

    if conf.FOOTER:
        try:
            logging.info('HANDLER - Fetching footerfile')
            footer_file = open(conf.FOOTER, 'r')
            footer = "".join(footer_file.readlines())
        except(IOError):
            logging.critical('HANDLER - Footerfile could not be opened')
            return 0
    else:
        footer = ""
    
    logging.info('HANLDER - {} fetched'.format(len(messages)))
    for ID, msg in messages:
        logging.info('HANDLER - reached {} <{}>'.format(ID, msg['subject']))
        match_obj = matched(msg, conf.KEEP_ATTACHMENT, footer=footer)
        if (diff and (match_obj.is_matched) != (conf.INPUTMAILBOX == 'matched')) or not diff:
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
    connector.cleanup()
