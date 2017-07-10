# coding=utf-8
# !/usr/bin/env python3.5

from connector import remote_connector, local_connector
from matched import matched

from config import REPORT_RECIPIENTS, INPUTMAILBOX, REPLYTO_ADRESS

import argparse
import os


def main(connector):
    if not 'INBOX' == INPUTMAILBOX:
        print("{} IS NOT A VALID MAILBOX FOR PRODUCTIV USE".format(INPUTMAILBOX))
        return 0

    messages = connector.fetch_all()
    for ID, msg in messages:
        match_obj = matched(msg)
        if match_obj.is_matched:
            msg = match_obj.msg_response()
            msg['from'] = "noreply@frobese.de"
            msg['to'] = match_obj.recipient
            msg.add_header('bcc', ", ".join(REPORT_RECIPIENTS))
            msg.add_header('reply-to', REPLYTO_ADRESS)
            if not connector.sendmail(msg):
                break

        report_msg = match_obj.msg_response(report=True)
        report_msg['from'] = "absentia@frobese.de"
        report_msg['to'] = ", ".join(REPORT_RECIPIENTS)
        if connector.sendmail(report_msg):
            if match_obj.is_matched:
                connector.move(ID, 'matched')
            else:
                connector.move(ID, 'unmatched')
        else:
            print("{} could not be send".format(report_msg['subject']))
    connector.cleanup()


def debug(connector, step, diff):
    messages = connector.fetch_all()
    for ID, msg in messages:
        match_obj = matched(msg)
        if (diff and (match_obj.is_matched) == (INPUTMAILBOX == 'matched')) or not diff:
            print("MAILBOX: {}".format(INPUTMAILBOX))
            print(match_obj.debug_output())
            if step:
                inp = input()
                if (inp == 'move' and not (
                        (INPUTMAILBOX == 'matched') == match_obj.is_matched)):
                    if match_obj.is_matched:
                        connector.move(ID, 'matched')
                    else:
                        connector.move(ID, 'unmatched')
                elif inp == 'move':
                    print("MOVE FROM: {} TO {} NOT VALID".format(
                        INPUTMAILBOX,
                        'matched' if match_obj.is_matched else 'unmatched'))
                    input()
                elif inp == 'abort':
                    break
            os.system('clear')
    connector.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="IMAP/STMP script handling absence messages, commands marked with [DEBUG] trigger the debug mode")
    parser.add_argument(
        '-d', dest='debug', action='store_const', const=True,
        default=False, help="run the script in debug mode")
    parser.add_argument(
        '-s', dest='step', action='store_const', const=True,
        default=False, help="[DEBUG] steps each mail")
    parser.add_argument(
        '--diff', dest='diff', action='store_const', const=True,
        default=False, help="[DEBUG] only shows wrongly assigned mails from matched or unmachted")
    parser.add_argument(
        '-l', dest='local', action='store_const', const=True,
        default=False, help="loads mails from TEST_DATA folder, send mails are displayed")

    argset = parser.parse_args()
    connector = remote_connector() if not argset.local else local_connector()
    connector.connect()
    if argset.debug or argset.step or argset.diff:
        debug(connector, argset.step, argset.diff)
    else:
        main(connector)
    connector.disconnect()
