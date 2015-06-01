import sqlite3
from helpers import Singleton
from helpers.decorators import cursor_op
from collections import namedtuple
from config import info

class ReviewBase(metaclass=Singleton):

    TABLE = 'reviews'

    def __init__(self, filename='reviews.db'):
        self.table = 'reviews'
        self.connection = sqlite3.connect(filename)
        self.connection.row_factory = sqlite3.Row
        self._create_table()

    @cursor_op
    def _create_table(self, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS {} (
            id INTEGER NOT NULL,
            author VARCHAR NOT NULL,
            bottle VARCHAR,
            date INTEGER NOT NULL,
            permalink VARCHAR NOT NULL,
            score INTEGER,
            subreddit VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            PRIMARY KEY (id)
        )'''.format(ReviewBase.TABLE))
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS review ON {}(user, url)'.format(ReviewBase.table))
        db.commit()

    @cursor_op
    def insert(self, review, cursor):
        ''' Insert a new Review into the database

            Args:
                review: a dictionary containing the right columns (see table definition)
                cursor: sqlite3.Cursor passed by decorator
        '''
        try:
            cursor.execute(
                'INSERT INTO {} VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)'
                .format(ReviewBase.TABLE),
                (
                    review['author'], review['bottle'], review['date'], review['permalink'],
                    review['score'], review['permalink'], review['title']
                )
            )
        except sqlite3.IntegrityError:
            logging.info('Review ({}) already exists in database.'.format(review.permalink))
        except:
            logging.exception('Unable to add review to database.')
        else:
            db.commit()


    @cursor_op
    def select(self, author, cursor, subreddit=None):
        ''' Select Reviews from the database matching criteria

            Args:
                user     : (string) The author of the review
                subreddit: ([string]) The subreddit in which the review was posted
                cursor   : sqlite3.Cursor passed by decorator
            Returns:
                A generator of reviews (dict) matching the criteria.
        '''
        if not subreddit:
            cursor.execute(
                'SELECT * FROM {} WHERE author = ? ORDER BY date DESC'
                .format(ReviewBase.TABLE),
                (author,)
            )
        else:
            cursor.execute('''
                SELECT * FROM {} WHERE author = ?
                 AND subreddit = ?
                 ORDER BY date DESC
                '''.format(ReviewBase.TABLE),
                (author,subreddit.lower())
            )

        for row in cursor:
            yield row
