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
    connector.init_mboxes()

    messages = connector.fetch_unawnsered()
    logging.info('HANDLER - {} fetched'.format(len(messages)))
    for ID, msg in messages:
        logging.info('HANDLER - reached {} <{}>'.format(ID, msg['subject']))
        match_obj = matched(msg, conf.KEEP_ATTACHMENT, conf.FOOTER)
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
            if not connector.sendmail(report_msg):
                logging.error(
                    'HANDLER - error while sending report for {}'.format(ID))
        else:
            logging.warning(
                    'HANDLER - no report recipients were configured')

        if match_obj.is_matched:
            connector.move(ID, conf.POSITIVE_BOX)
        else:
            connector.move(ID, conf.NEGATIVE_BOX)
    logging.debug('HANDLER - done.')
    connector.cleanup()


def debug(connector, conf, step, diff):
    messages = connector.fetch_all()

    logging.warning('HANDLER - Running in debug mode')
    
    logging.info('HANLDER - {} fetched'.format(len(messages)))
    for ID, msg in messages:
        logging.info('HANDLER - reached {} <{}>'.format(ID, msg['subject']))
        match_obj = matched(msg, conf.KEEP_ATTACHMENT, conf.FOOTER)
        if (diff and (match_obj.is_matched) != (conf.INPUTMAILBOX == conf.POSITIVE_BOX)) or not diff:
            print("MAILBOX: {}".format(conf.INPUTMAILBOX))
            print(match_obj.debug_output())
            if step:
                inp = input()
                if (inp == 'move' and not (
                        (conf.INPUTMAILBOX == conf.POSITIVE_BOX) == match_obj.is_matched)):
                    if match_obj.is_matched:
                        connector.move(ID, conf.POSITIVE_BOX)
                    else:
                        connector.move(ID, conf.NEGATIVE_BOX)
                elif inp == 'move':
                    print("MOVE FROM: {} TO {} NOT VALID".format(
                        conf.INPUTMAILBOX,
                        conf.POSITIVE_BOX if match_obj.is_matched else conf.NEGATIVE_BOX))
                    input()
                elif inp == 'abort':
                    break
            os.system('clear')
    connector.cleanup()
