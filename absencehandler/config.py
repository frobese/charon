# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8

from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG

try:
    from absencehandler.conf_local import *
except ImportError:
    pass

# IMAP and SMTP HOST
HOST = "www.frobese.de"
# IMAP Port
IMAP_PORT = 993
#SMTP Port
SMTP_PORT = 587

# IMAP and SMTP credentials
# USERNAME = "doe"
# PASSWORD = "johnsmailbox123"


# Inbox on which the main loop shall work
INPUTMAILBOX = "INBOX"

# Recipients of the Report Messages
REPORT_RECIPIENTS = [
    "nbomsdorf@frobese.de", "singelmann@frobese.de",
    "hgoedeke@frobese.de", "smeyer@frobese.de"
]

# Logging
LOG_LEVEL = DEBUG # [ CRITICAL | ERROR | WARNING | INFO | DEBUG ]
LOG_DIR = "/tmp"

# Origin Adress if the Mail response
ORIG_ADRESS = "noreply@frobese.de"
# Mailadress thats set as the "reply to"
REPLYTO_ADRESS = "hgoedeke@frobese.de"

# Testing stuff
TEST_DATA = "./subset"
