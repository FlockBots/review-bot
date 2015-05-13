import praw

class Editable:
    """ 
    Helper class to contain similar attributes for PRAW comments and submission
    """

    Submission = 'submission'
    Comment    = 'comment'
    Message    = 'message'

    def __init__(self, editable):
        self.original  = editable
        self.id        = editable.id
        self.author    = editable.author
        if isinstance(editable, praw.objects.Comment):
            self._set_comment_properties(editable)
        elif isinstance(editable, praw.objects.Submission):
            self._set_submission_properties(editable)
        elif isinstance(editable, praw.objects.Message):
            self._set_message_properties(editable)
        else:
            raise ValueError("Editable is not a PRAW message, comment or submission")

    def _set_comment_properties(self, editable):
        self.reply = editable.reply
        self.text  = editable.body
        self.type  = Editable.Comment
        self.permalink  = editable.permalink
        self.submission = editable.submission
        self.subreddit  = editable.subreddit

    def _set_submission_properties(self, editable):
        self.reply = editable.add_comment
        self.text  = editable.self_text
        self.type  = Editable.Submission
        self.permalink  = editable.permalink
        self.submission = self.original
        self.subreddit  = editable.subreddit

    def _set_message_properties(self, editable):
        self.reply = editable.reply
        self.text  = editable.body
        self.type  = Editable.Message
        self.permalink  = editable.permalink
        self.submission = None
        self.subreddit  = editable.subreddit 

