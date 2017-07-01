# coding=utf-8
# !/usr/bin/env python3.5

from connector import imap_connector, smtp_connector, local_connector
from matched import matched

from config import REPORT_RECIPIENTS, MOVE, INPUTMAILBOX, REPLYTO_ADRESS

import argparse
import os


def main(debug, step, local):
    debug = ('matched' in INPUTMAILBOX or step)

    if local:
        iconn = local_connector()
        sconn = iconn
    else:
        iconn = imap_connector()
        sconn = smtp_connector()

    iconn.connect()
    sconn.connect()

    messages = iconn.fetch_all()
    for ID, msg in [(key, messages[key]) for key in sorted(
            messages.keys(), key=lambda item: int(item), reverse=True)]:
        match_obj = matched(msg)
        if not debug:
            if match_obj.is_matched:
                msg = match_obj.msg_response()
                msg['from'] = "noreply@frobese.de"
                msg['to'] = match_obj.recipient
                msg.add_header('reply-to', REPLYTO_ADRESS)
                if not sconn.sendmail(msg):
                    break

            report_msg = match_obj.msg_response(report=True)
            report_msg['from'] = "absentia@frobese.de"
            report_msg['to'] = ", ".join(REPORT_RECIPIENTS)
            if sconn.sendmail(report_msg):
                if match_obj.is_matched and MOVE:
                    iconn.move(ID, 'matched')
                elif MOVE:
                    iconn.move(ID, 'unmatched')
            else:
                print("{} could not be send".format(report_msg['subject']))
        else:
            print("MAILBOX: {}".format(INPUTMAILBOX))
            print(match_obj.debug_output())
            if step and "," in match_obj.results['EMPLOYEE'][0]:
                inp = input()
                if (inp == 'move' and MOVE and not (
                        (INPUTMAILBOX == 'matched') == match_obj.is_matched)):
                    if match_obj.is_matched:
                        iconn.move(ID, 'matched')
                    else:
                        iconn.move(ID, 'unmatched')
                elif inp == 'move':
                    print("MOVE SETTING:{}, FROM: {} TO {}".format(
                        MOVE, INPUTMAILBOX,
                        'matched' if match_obj.is_matched else 'unmatched'))
                    input()
                elif inp == 'abort':
                    break
                os.system('clear')

    if MOVE:
        iconn.cleanup()
    iconn.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="IMAP/STMP script handling absence messages")
    parser.add_argument(
        '-d', dest='debug', action='store_const', const=True,
        default=False, help="run the script in debug mode")
    parser.add_argument(
        '-s', dest='step', action='store_const', const=True,
        default=False, help="run the script in debug mode and steps each mail")
    parser.add_argument(
        '-l', dest='local', action='store_const', const=True,
        default=False, help="loads mails from TEST_DATA folder, send mails are displayed")

    argset = parser.parse_args()
    main(argset.debug, argset.step, argset.local)
