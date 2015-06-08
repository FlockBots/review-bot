import sqlite3
from helpers import Singleton
from helpers.decorators import cursor_op
import logging

class ReviewBase(metaclass=Singleton):

    TABLE = 'reviews'

    def __init__(self, filename):
        self.logger = logging.getLogger(__name__)
        self.table = 'reviews'
        self.connection = sqlite3.connect(filename)
        self.connection.row_factory = sqlite3.Row
        self._create_table()

    @cursor_op
    def _create_table(self, cursor):
        self.logger.debug('Creating table {}'.format(ReviewBase.TABLE))
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
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS review ON {}(author, permalink)'.format(ReviewBase.TABLE))
        self.connection.commit()

    @cursor_op
    def insert(self, review, cursor):
        """ Insert a new Review into the database

            Args:
                review: a dictionary containing the right columns (see table definition)
                cursor: sqlite3.Cursor passed by decorator
        """
        self.logger.debug('Inserting review ({title} by {author})'.format(**review))
        try:
            cursor.execute(
                'INSERT INTO {} VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)'
                .format(ReviewBase.TABLE),
                (
                    review['author'], review['bottle'], review['date'], review['permalink'],
                    review['score'], review['subreddit'], review['title']
                )
            )
        except sqlite3.IntegrityError:
            self.logger.info('Review ({}) already exists in database.'.format(review.permalink))
        except:
            self.logger.exception('Unable to add review to database.')
        else:
            self.connection.commit()

    @cursor_op
    def update_or_insert(self, review, cursor):
        self.logger.debug('Updating review ({title} by {author})'.format(**review))
        if self.select(author=review['author']):
            try:
                cursor.execute(
                    '''UPDATE {} SET bottle=?, score=?
                       WHERE author=? AND (title=? OR permalink=?)'''
                      .format(ReviewBase.TABLE),
                    (review['bottle'], review['score'], review['author'],
                        review['title'], review['permalink'])
                )
            except:
                self.logger.exception('Unabe to update review.')
            else:
                self.connection.commit()
        else:
            self.insert(review)


    @cursor_op
    def select(self, author, cursor, subreddit=None):
        """ Select Reviews from the database matching criteria

            Args:
                user     : (string) The author of the review
                subreddit: ([string]) The subreddit in which the review was posted
                cursor   : sqlite3.Cursor passed by decorator
            Returns:
                A generator of reviews (dict) matching the criteria.
        """
        self.logger.debug('Selecting review by {} (subreddit: {})'.format(author, subreddit))
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
        return cursor.fetchall()
