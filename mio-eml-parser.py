#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
#import six

import os
import sys
import argparse
import traceback
import pickle
import logging
import logging.handlers
import time
import io
import pprint

# for email
import email
import email.parser
import email.policy
from email.message import EmailMessage
from email.header import Header
from email.mime.text import MIMEText

# for pop3
import poplib
import email
#import dateutil.tz
import datetime

APPLICATION_NAME = "emlparser"
stdout_fmt = '%(asctime)s %(levelname)s %(name)s - %(message)s'
file_fmt   = '%(asctime)s %(process)d %(levelname)s %(name)s:%(funcName)s(%(filename)s:%(lineno)d) - %(message)s'

def parse_date(msg):
    m_date = msg.get('Date')
    t_date = email.utils.parsedate_tz(m_date)
    #tz = dateutil.tz.tzoffset(None, t_date[9])
    #d_date = datetime.datetime(*t_date[:6], tzinfo=tz)
    d_date = datetime.datetime(*t_date[:6])
    return d_date.isoformat()

def parse_message(eml):
    msg = email.parser.BytesParser(policy=email.policy.default).parse(eml)
    date = parse_date(msg)
    subject = msg.get('Subject')
    mailfrom = msg.get('From').addresses[0].addr_spec
    body = msg.get_body(preferencelist=('plain', 'html'))
    #charset = msg.get_param('charset')
    c = body.get_content()
    return date, subject, mailfrom, c

def getcontents(c):
    r = {}
    for l in c.splitlines():
        l = l.replace(chr(0x3000), ' ')
        
        k = "出欠"
        if l.find("【ご出席") >= 0 and not k in r:
            r[k] = l

        k = "所属"
        if l.find("○ご所属・ご役職") >= 0 and not k in r:
            r[k] = l

        k = "電話"
        if l.find("○お電話：") >= 0 and not k in r:
            r[k] = l

        k = "出身"
        if l.find("○出身学部・学科：") >= 0 and not k in r:
            r[k] = l

        k = "入社年次"
        if l.find("○入社年次") >= 0 and not k in r:
            r[k] = l

        k = "名簿"
        if l.find("名簿への掲載を希望しない") >= 0 and not k in r:
            r[k] = l.replace(" ", '')

        k = "名簿項目"
        if l.find("名簿への掲載を希望しない項目") >= 0 and not k in r:
            r[k] = l.replace(" ", '')
            
        k = "mail"
        if l.find("○e-mail") >= 0 and not k in r:
            r[k] = l.replace(" ", '')
    return r

def process_emails(args):
    # pop3 login
    emails = args.eml
    numMessages = len(emails)
    logger.info("%s messages." % numMessages)
    
    # get email, insert gmail
    try:
        for eml in emails:
            d, s, mailfrom, body = parse_message(eml)
            r = getcontents(body)
            print(mailfrom)
            import yaml
            pprint.pprint(r)
            print("-"*80)
            #raw_input("Type 'Ctrl+C' if you want to interrupt program.")
    except Exception as e:
        logger.exception('Failed to import messages')
        raise

def main():
    try:
        process_emails(args)
    except KeyboardInterrupt:
        sys.exit("Crtl+C pressed. Shutting down.")
    except Exception as e:
        logger.exception('Unknown exception occured.')
        sys.exit("Unknown exception occured. Shutting down.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MIO e-mail response parser')
    parser.add_argument('eml', nargs='+', type=argparse.FileType('rb'), help='input emls')
    parser.add_argument('-d', '--debug',  action="store_true", help="Enable debug message.")
    parser.set_defaults(logging_level='INFO')

    args = parser.parse_args()

    # set logger
    _lvl = args.logging_level
    if args.debug:
        _lvl = logging.DEBUG
        httplib2.debuglevel = 4
    
    _cformatter = logging.Formatter(stdout_fmt)
    _ch = logging.StreamHandler()
    _ch.setLevel(logging.INFO)
    _ch.setFormatter(_cformatter)
    _file_formatter = logging.Formatter(file_fmt)
    _fh = logging.handlers.RotatingFileHandler(APPLICATION_NAME + '.log', maxBytes=1024 * 1024 * 8, backupCount=8)
    _fh.setLevel(logging.DEBUG)
    _fh.setFormatter(_file_formatter)
    logger = logging.getLogger(APPLICATION_NAME)
    logger.setLevel(_lvl)
    logger.addHandler(_ch)
    logger.addHandler(_fh)

    logger.debug(args)
    logger.debug('logging level: %s' % logger.getEffectiveLevel())

    main()
