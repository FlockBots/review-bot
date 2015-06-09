from modules import ReviewBase
from config import info
from archive_parser import Parser
import logging
import os
import time
from datetime import datetime
import app
import argparse

def parse(skip=0):
    parser = Parser(info['archive_file'])
    if _file_age(info['archive_file']).days > 1:
        parser.download(info['archive_key'])
    review_db = ReviewBase(info['database_filename'])

    for row, submission in parser.get_submissions(skip):
        review = {
            'author': row['user'].lower(),
            'bottle': row['whisky'],
            'date'  : row['date'].strftime('%Y%m%d'),
            'permalink' : submission.permalink,
            'score': row['score'],
            'subreddit': submission.subreddit.display_name.lower(),
            'title': submission.title
        }
        review_db.update_or_insert(review)

def _file_age(filename):
    """ Get the age of a file
        Args:
            filename: path to the file
        Returns:
            datetime.timedelta object
    """
    if not os.path.isfile(filename):
        raise ValueError('`{}` does not lead to an existing file.'.format(filename))
    file_ctime = time.ctime(os.path.getctime(filename))
    file_datetime = datetime.strptime(file_ctime, "%a %b %d %H:%M:%S %Y")
    return datetime.now() - file_datetime

def set_commandline_args():
    parser = argparse.ArgumentParser(description='Parse the Reddit Whisky Review Archive.')
    parser.add_argument('--log', '-l', default='info',
                       help='Set the log level to debug or info.')
    parser.add_argument('--skip', '-s', type=int, default=0,
                       help='Skip the first n rows of the archive.')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = set_commandline_args()
    level = logging.INFO
    if args.log == 'debug':
        level = logging.DEBUG
    app.set_logging(info['log_filename'], level)
    logger = logging.getLogger(__name__)
    logger.debug('Logging in debug mode.')
    parse(args.skip)
