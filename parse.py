from modules import ReviewBase
from config import info
from archive_parser import Parser
import logging
import os
import time
from datetime import datetime
import app
import argparse
import functools
import re

def parse(skip=0, filter_date=None):
    parser = Parser(info['archive_file'])
    if _file_age(info['archive_file']).days > 1:
        parser.download(info['archive_key'])
    review_db = ReviewBase(info['database_filename'])

    if not filter_date:
        filter_date = '01/01/1970'
    filter_date = parser.parse_date(filter_date)
    logger.info('Skipping reviews entered before {}.'.format(str(filter_date)))
    review_filter = functools.partial(
        _new_review_filter,
        review_db=review_db,
        filter_date=filter_date
    )
    archive = parser.get_submissions(skip=skip, row_filter=review_filter)
    for row, submission in archive:
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


def _new_review_filter(row, review_db, filter_date):
    try:
        delta = filter_date - row['archived']
    except TypeError:
        logging.error('No archival date.')
    else:
        if delta.days > 0:
            return True
    if not row['date']:
        return False
    formatted_date = row['date'].strftime('%Y%m%d')
    stored_reviews = review_db.execute(
        'SELECT * FROM {} WHERE author = ? AND (permalink = ? OR date = ?)'
        .format(ReviewBase.TABLE), (row['user'].lower(), row['url'], formatted_date)
    )
    if not stored_reviews:
        return False
    for stored in stored_reviews:
        if not stored['bottle']:
            return False
    return True


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
    parser = argparse.ArgumentParser(
        description='Parse the Reddit Whisky Review Archive.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--debug', action='store_true',
                       help='Set the log level to DEBUG.')
    parser.add_argument('--skip', type=int, default=0, metavar='N',
                       help='Skip the first n rows of the archive.')
    parser.add_argument('--filter-date', metavar='DATE', default='01/01/1970',
                        help="Skip reviews older than the given date (mm/dd/YYYY).")

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = set_commandline_args()
    level = logging.INFO
    if args.debug:
        level = logging.DEBUG
    app.set_logging(info['log_filename'], level)
    logger = logging.getLogger(__name__)
    logger.debug('Logging in debug mode.')
    parse(args.skip, args.filter_date)