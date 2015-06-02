import sqlite3
import logging
from helpers.decorators import cursor_op
from helpers import Singleton

class Database(metaclass=Singleton):

    comment_table = 'editables'

    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.logger = logging.getLogger(__name__)
        self._create()

    @cursor_op
    def _create(self, cursor):
        """ Creates the necessary tables if they do not exists """
        self.logger.debug('Creating table ({})'.format(Database.comment_table))
        query = (
            'CREATE TABLE IF NOT EXISTS {} '
            '(id TEXT PRIMARY KEY)'
        ).format(Database.comment_table)
        cursor.execute(query)
        self.connection.commit()

    @cursor_op
    def store_editable(self, editable, cursor):
        """ Stores the editable id in the database

        To prevent the bot from revisiting comments,
        save the parsed editable id in the database.

        Args:
            editable: PRAW comment, submission or message
        """
        self.logger.debug('Storing editable ({})'.format(editable.id))
        query = 'INSERT INTO {} VALUES (?)'.format(Database.comment_table)
        cursor.execute(query, (editable.id,))
        self.connection.commit()

    @cursor_op
    def get_editable(self, editable, cursor):
        """ Gets the values of editable stored in the database

        Args:
            editable: PRAW comment, submission or message
        Returns:
            If editable exists:
                A tuple of the data in the columns
            Otherwise:
                None
        """
        self.logger.debug('Selecting editable ({})'.format(editable.id))
        query = 'SELECT * FROM {} WHERE id = ?'.format(Database.comment_table)
        cursor.execute(query, (editable.id,))
        row = cursor.fetchone()
        return row
