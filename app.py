import praw
import re
from helpers import Database
from helpers import Editable
from config import info
from config import credentials
from bot import Bot
import time
import sys
import logging


def set_logging(log_filename, level=logging.INFO):
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='{asctime} | {name:<8.8} | {levelname:<8.8} | {message}',
        style='{'
    )
    logging.getLogger().addHandler(logging.StreamHandler())
    requests_logger = logging.getLogger('requests')
    requests_logger.setLevel(logging.WARNING)


def run():
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        set_logging(info['log_filename'], logging.DEBUG)
        print('running with logging on Debug')
    else:
        set_logging(info['log_filename'])

    reddit = praw.Reddit(info['useragent'])
    reddit.login(credentials['username'], credentials['password'])
    database = Database(info['database_filename'])
    bot = Bot(reddit, database, footer='')

    register_modules()

    while True:
        bot.check_messages(mark_read=True)
        time.sleep(60)


def register_modules():
    ''' Imports all modules that need to be registered by the Bot '''
    from modules import list_reviews
