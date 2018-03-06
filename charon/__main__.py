try:
    from charon.connector import remote_connector, local_connector
    from charon.matched import matched
    from charon.charon import prod, debug
    from charon.config import config
except ImportError:
    from connector import remote_connector, local_connector
    from matched import matched
    from charon import prod, debug
    from config import config

from logging import handlers
from time import gmtime, strftime

import argparse
import os
import logging
import sys

def main():
    parser = argparse.ArgumentParser(
        description="IMAP/STMP script handling absence messages, commands marked with [DEBUG] trigger the debug mode")
    parser.add_argument(
        '-d', dest='debug', action='store_const', const=True,
        default=False, help="run the script in debug mode")
    parser.add_argument(
        '--crconf', dest='crconf', action='store_const', const=True,
        default=False, help="create conf in user homedir")
    parser.add_argument(
        '-s', dest='step', action='store_const', const=True,
        default=False, help="[DEBUG] steps each mail")
    parser.add_argument(
        '--diff', dest='diff', action='store_const',
        const=True, default=False,
        help="[DEBUG] only shows wrongly assigned mails from matched or unmachted")
    parser.add_argument(
        '-l', dest='local', metavar='PATH', type=str,help="loads mails from PATH, send mails are displayed")

    argset = parser.parse_args()

    if argset.crconf:
        print("Creating Logfile ...")
        try:
            conf = config(True)
            print("OK!")
        except:
            print("Error!")
    else:
        try:
            conf = config()
        except:
            print("There is no config in ~/.charon.cfg")
            return 1

        logfile = "{}/charon.log".format(
                conf.LOCATION)
        handler = handlers.TimedRotatingFileHandler(
            logfile, when='midnight', backupCount=14
        )
        handler.setFormatter(logging.Formatter("%(relativeCreated)5d -- [%(levelname)s] %(message)s"))
        handler.setLevel(conf.LEVEL)
        # logging.basicConfig(evel=conf.LEVEL, format="%(asctime)s -- [%(levelname)s] %(message)s", handler=handler)
        logging.root.setLevel(conf.LEVEL)
        logging.root.addHandler(handler)
        # logging.getLogger

        logging.info("TIME OF EXEC {}".format(strftime("%H:%M:%S %Y-%m-%d", gmtime())))

        connector = remote_connector(conf) if not argset.local else local_connector(conf, argset.local)
        connector.connect()
        if argset.debug or argset.step or argset.diff:
            debug(connector, conf, argset.step, argset.diff)
        else:
            prod(connector, conf)
        connector.disconnect()

if __name__ == "__main__":
    main()