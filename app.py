import praw
from helpers import Database
from config import info
from config import credentials
from bot import Bot
from modules import ReviewBase
import time
import sys
import logging
from modules import list_reviews
from modules import classify_incoming

def set_logging(log_filename, level=logging.INFO):
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='{asctime} | {name:<8.8} | {levelname:<8.8} | {message}',
        style='{'
    )
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    requests_logger = logging.getLogger('requests')
    requests_logger.setLevel(logging.WARNING)
    return logger


def run():
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        logger = set_logging(info['log_filename'], logging.DEBUG)
        logging.info('running with logging on Debug')
    else:
        logger = set_logging(info['log_filename'])

    reddit = praw.Reddit(info['useragent'])
    reddit.login(credentials['username'], credentials['password'])
    database = Database(info['database_filename'])
    bot = Bot(reddit, database, footer='')

    register_modules(bot)

    while True:
        num_messages_read = bot.check_messages(mark_read=True)
        for sub in info['review_subs']:
            bot.check_comments(sub)
        if num_messages_read < 3:
            time.sleep(300)
        else:
            time.sleep(60)


def register_modules(bot):
    """ Imports all modules that need to be registered by the Bot """
    review_db = ReviewBase(info['database_filename'])
    list_cb = list_reviews.register(review_db)
    classify_cb = classify_incoming.register(review_db)

    for callback in list_cb:
        bot.register_trigger(callback)
    for callback in classify_cb:
        bot.register_general(callback)

if __name__ == '__main__':
    run()
