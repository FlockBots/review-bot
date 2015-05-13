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
        format = '{asctime} | {name:<8.8} | {levelname:<8.8} | {message}',
        style='{'
    )
    logging.getLogger().addHandler(logging.StreamHandler())
    requests_logger = logging.getLogger('requests')
    requests_logger.setLevel(logging.WARNING)

def run():
    while True:
        for subreddit in info['subreddits']:
            bot.check_comments(subreddit)
            bot.check_submissions(subreddit)
        bot.check_messages()
        time.sleep(60)

reddit = praw.Reddit(info['useragent'])
reddit.login(credentials['username'], credentials['password'])
database = Database(info['database_filename'])
bot = Bot(reddit, database, footer='')

if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    set_logging(info['log_filename'], logging.DEBUG)
    print('running with logging on Debug')
else:
    set_logging(info['log_filename'])

@bot.register_regex(r'\.nsfw')
@bot.make_reply
def mark_nsfw(editable, match):
    """ Set NSFW tag on the submission of the editable
        if the editable contains '.status sold'
    """
    if editable.type == Editable.Message:
        return 'You cannot set messages to NSFW.'
    else:
        submission = editable.submission
        if not editable.author == submission.author:
            return "You cannot mark someone else's submission as NSFW."
        submission.mark_as_nsfw()
        return "You're submission has been marked as NSFW!"