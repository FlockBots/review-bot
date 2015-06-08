from modules import ReviewBase
from config import info
from archive_parser import Parser
import logging

def parse():
    parser = Parser(info['archive_file'])
    parser.download(info['archive_key'])
    review_db = ReviewBase(info['database_filename'])
    logger = logging.getLogger(__name__)

    for row, submission in parser.get_submissions():
        review = {
            'author': submission.author,
            'bottle': row['whisky'],
            'date'  : row['date'],
            'permalink' : submission.permalink,
            'score': row['score'],
            'subreddit': submission.subreddit.display_name.lower(),
            'title': submission.title
        }
        logger.debug('Review: {author}, {bottle}'.format(**review))
        review_db.update_or_insert(review)
