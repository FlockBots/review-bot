import re
from helpers.decorators import rate_limited
from helpers import Editable
from helpers import Singleton
from config import info
from collections import namedtuple
import logging


Callback = namedtuple('Callback', ['regex', 'function'])


class Bot(metaclass=Singleton):
    def __init__(self, reddit, database, footer=''):
        # Stores callbacks for specific bot calls.
        self.trigger_callbacks = {}

        # Stores callbacks for when patterns are recognised in a comment.
        self.general_callbacks = {}

        # Stores the last visited comments of a subreddit.
        self.last_visited = {}

        self.reddit = reddit
        self.database = database
        self.footer = footer or "___\n^(Hey I'm a bot! Please address any remarks to {}.)".format(info['owner'])
        self.reply_text = ''
        self.logger = logging.getLogger(__name__)

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
            if self.check_callbacks(editable, self.trigger_callbacks) or mark_read:
                message.mark_as_read()
                total_read += 1
            self.database.store_editable(editable)
        return total_read

    def check_comments(self, subreddit):
        if len(self.general_callbacks) == 0:
            return
        last_comment = self.last_visited.get(subreddit, None)
        comments = self.reddit.get_comments(
            subreddit=subreddit,
            place_holder=last_comment,
            limit=10
        )
        for comment in comments:
            editable = Editable(comment)
            self.check_callbacks(editable, self.general_callbacks)
            if self.database.get_editable(comment):
                continue

            self.check_callbacks(editable, self.trigger_callbacks)
            self.database.store_editable(editable)

    def check_callbacks(self, editable, callbacks):
        """ Iterates over registered callbacks

            If the editable contains text that triggers a registered callback,
            it calls that functions with the editable and matched text
            as the arguments.

            Args:
                editable: (helper.Editable) the editable to check for triggers
                callbacks: dictionary of callbacks. Key: regex, value: function
            Returns:
                True, when a callback was triggered
                False, otherwise
        """
        has_callback = False
        for regex, functions in callbacks.items():
            string = editable.text
            match = re.findall(regex, string, re.IGNORECASE)
            if match:
                logging.debug('Matching `{regex}` on `{string}`'
                              .format(regex=regex, string=string))
                has_callback = True
                for callback in functions:
                    reply = callback(editable, match)
                    if isinstance(reply, str):
                        self.build_reply(reply)
        if has_callback:
            self.reply_to(editable)
        return has_callback

    def register_trigger(self, callback):
        (self.trigger_callbacks.setdefault(callback.regex, [])
            .append(callback.function))

    def register_general(self, callback):
        (self.general_callbacks.setdefault(callback.regex, [])
            .append(callback.function))

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
    def reply_to(self, editable, text=None):
        """ Comments on the object

            Args:
                editable: (helper.Editable) the editable to reply to
                text: (string) markdown message to put in the comment
        """
        self.build_reply(text)
        if not self.reply_text:
            return
        self.reply_text += self.footer
        self.logger.debug('Reply {id}: {msg}'.format(
            id=editable.id, msg=self.reply_text)
        )
        editable.reply(self.reply_text)

        # reset reply text
        self.reply_text = ''

    def __repr__(self):
        string = ''
        if self.reddit.is_logged_in:
            string += '(authenticated) '
        else:
            string += '(unauthenticated) '
        string += self.footer
        return string
