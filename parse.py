from modules import ReviewBase
from config import info
from archive_parser import Parser

def parse():
    parser = Parser(info['archive_file'])
    parser.download(info['archive_key'])
    review_db = ReviewBase(info['database_filename'])

    for row, submission in Parser.get_submissions():
        review = {
            'author': submission.author,
            'bottle': row['whisky'],
            'date'  : row['date'],
            'permalink' : submission.permalink,
            'score': row['score'],
            'subreddit': submission.subreddit.display_name.lower(),
            'title': submission.title
        }
        review_db.insert_or_update(review)

