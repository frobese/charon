# Charon
Lightweight adaptable Mailparser

When triggered Charon connects to a given Mail server via IMAP and SMTP and looks up all unanswered messages in the set IMAP folder.  
If an sufficient match was found a response is composed and send, in any case an report is composed and send to all configured recipients.
In the end a copy of the original message is created in the IMAP folders `matched` and `unmatched` which *have* to be existent.

## Requirements
* [Python3.4](https://www.python.org/download/releases/3.4.0/)
* [PIP3](https://pypi.python.org/pypi/pip)

## Installation
1. Run `$ pip3 install charon-x.x.x.tar.gz`
2. Create a config file (`.charon.cfg`) with `$ charon --crconf` which is placed in the home dir of the current user.

    A default config looks like this:

        [GENERAL]
        keep_attachment = false
        reply_to = james.doe@example.com
        origin = noreply@example.com
        report_recipients = john.doe@example.com, jane.doe@example.com
        footer_path = None
    
    `keep_attachment` determines if the **first** occurrence of an **pdf** attachment in the MIME-Tree is passed on in the response.  
    `reply_to` holds the mail address that is used in the reply to field for the response.  
    `origin` sets the mail address the response and report shall originate from.  
    `report_recipients` the recipients for the report messages.  
    `footer_path` contains the path to the text file containing the footer which will be appended to the message ending.

        [MAIL]
        smtp_port = 587
        username = jdoe
        host = www.example.com
        inputmailbox = INBOX
        password = secret123
        imap_port = 993

        [LOG]
        level = INFO
        location = /tmp



**Important** At the moment the IMAP connection has to be IMAPv4 SSL and SMTP starttls
## Usage
The queried Mail-Account has to have a `matched` and `unmatched` folder in which the handled mails are placed accordingly.

The Footer used in the Mailresponse can be placed in any text-file and then configured in the config-file.

The Handler has to be triggered with `$ charon`, for example by cron.  
To prevent bugs the complete path should be referenced in the crontab, `$ which charon` shows it.