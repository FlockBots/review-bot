import re
import praw
from helpers import rate_limited
from helpers import Editable
from helpers import Singleton
from config import info
import logging


class Bot(metaclass=Singleton):
    def __init__(self, reddit, database, footer=''):
        self.regex_callbacks = {}
        self.reddit = reddit
        self.database = database
        self.footer = footer or "___\n^(Hey I'm a bot! Please address any remarks to {}.)".format(info['owner'])
        self.reply_text = None

    def check_messages(self, mark_read=False):
        """ Get the users unread messages
            and check for callback triggers.

            Args:
                mark_read: (bool) if True, mark the messages as read

            Returns:
                Number of messages read.
        """
        messages = self.reddit.get_unread(unset_has_mail=mark_read)
        total_read = 0
        for message in messages:
            if self.database.get_editable(message):
                continue
            editable = Editable(message)

            # if a callback was made, mark as read.
            if self.check_callbacks(editable) or mark_read:
                message.mark_as_read()
                total_read += 1
            self.database.store_editable(editable)
        return total_read

    def check_callbacks(self, editable):
        """ Iterates over registered callbacks

            If the editable contains text that triggers a registered callback,
            it calls that functions with the editable and matched text
            as the arguments.

            Args:
                editable: (helper.Editable) the editable to check for triggers
            Returns:
                True, when a callback was triggered
                False, otherwise
        """
        has_callback = False
        for regex, functions in self.regex_callbacks.items():
            string = editable.text
            match = re.match(regex, string)
            if match:
                has_callback = True
                for callback in functions:
                    callback(editable, match)
        self.reply(editable)
        return has_callback

    def register_regex(self, regex):
        """ Decorator to register callbacks """
        def wrapper(function):
            logging.debug('Registering callback at: ' + regex)
            try:
                self.regex_callbacks[regex].append(function)
            except KeyError:
                self.regex_callbacks[regex] = [function]
            return function
        return wrapper

    def make_reply(self, function):
        """ Decorator to let the bot reply
            Requires the function to return a string
        """
        def wrapper(*args, **kwargs):
            text = function(*args, **kwargs)
            if not isinstance(text, str):
                raise TypeError('Callback does not return a string.')
            self.build_reply(text)
        return wrapper

    def build_reply(self, text):
        if not text:
            return
        if not self.reply_text:
            self.reply_text = text
        else:
            self.reply_text += text
        # Add spacer
        self.reply_text += '\n___\n'

    @rate_limited
    def reply(self, editable, text=None):
        """ Comments on the object

            Args:
                editable: (helper.Editable) the editable to reply to
                text: (string) markdown message to put in the comment
        """
        self.build_reply(text)
        self.reply_text += self.footer
        logging.debug('Reply {id}: {msg}'.format(
            id=editable.id, msg=self.reply_text)
        )
        editable.reply(self.reply_text)
        self.reply_text = ''

    def __repr__(self):
        string = ''
        if self.reddit.is_logged_in:
            string += '(authenticated) '
        else:
            string += '(unauthenticated) '
        string += self.footer
        return string
