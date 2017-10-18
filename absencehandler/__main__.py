from absencehandler.connector import remote_connector, local_connector
from absencehandler.matched import matched
from absencehandler.absencehandler import prod, debug

from absencehandler.config import (LOG_LEVEL, LOG_DIR)

from datetime import datetime

import argparse
import os
import logging
import sys

def main():
    logfile = "{}/ah_log_{}.log".format(
            LOG_DIR, datetime.now().strftime("%d%m%y_%H%M"))
    logging.basicConfig(
        filename=logfile, level=LOG_LEVEL, format="[%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(
        description="IMAP/STMP script handling absence messages, commands marked with [DEBUG] trigger the debug mode")
    parser.add_argument(
        '-d', dest='debug', action='store_const', const=True,
        default=False, help="run the script in debug mode")
    parser.add_argument(
        '-s', dest='step', action='store_const', const=True,
        default=False, help="[DEBUG] steps each mail")
    parser.add_argument(
        '--diff', dest='diff', action='store_const',
        const=True, default=False,
        help="[DEBUG] only shows wrongly assigned mails from matched or unmachted")
    parser.add_argument(
        '-l', dest='local', action='store_const', const=True,
        default=False, help="loads mails from TEST_DATA folder, send mails are displayed")

    argset = parser.parse_args()
    connector = remote_connector() if not argset.local else local_connector()
    connector.connect()
    if argset.debug or argset.step or argset.diff:
        debug(connector, argset.step, argset.diff)
    else:
        prod(connector)
    connector.disconnect()

if __name__ == "__main__":
    main()