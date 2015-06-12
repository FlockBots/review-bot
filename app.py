import praw
from helpers import Database
from config import info
from config import credentials
from helpers import Bot
from modules import ReviewBase
from requests.exceptions import ConnectionError, HTTPError, Timeout
import time
import sys
import logging
from modules import list_reviews
from modules import classify_incoming

def set_logging(log_filename, level=logging.INFO):
    logging.basicConfig(
        filename=log_filename,
        level=level,
        format='{asctime:<19.19} | {name:<20.20} | {levelname:<6.6} | {message}',
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
        logger.info('running with logging on DEBUG.')
    else:
        logger = set_logging(info['log_filename'])
        logger.info('Running with logging on INFO.')

    reddit = praw.Reddit(info['useragent'])
    reddit.login(credentials['username'], credentials['password'])
    database = Database(info['database_filename'])
    bot = Bot(reddit, database, footer='')

    register_modules(bot)

    connection_error_count = 0
    # How long to wait before retrying at lost connection/busy Reddit.
    connection_timeout = 10 * 60
    while True:
        try:
            num_messages_read = bot.check_messages(mark_read=True)
            for sub in info['review_subs']:
                bot.check_comments(sub)
        except ConnectionError, HTTPError, Timeout:
            connection_error_count += 1
            if connection_error_count > 5:
                raise EnvironmentError('No connection available for {} seconds.'
                    .format(5 * connection_timeout))
            else:
                time.sleep(connection_timeout)
        except KeyboardInterrupt:
            logger.info('Quitting by keyboard interrupt.')
            return
        else:
            connection_error_count = 0
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
