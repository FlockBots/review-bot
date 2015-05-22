from bot import Bot

bot = Bot()  # Singleton, requires to be initialised before

# Register function below
# @bot.register_regex(r'my_regex')   -   Fires function if comment/submission matches regex
# @bot.make_reply                    -   Creates a reply using the returned string
# def callback(editable, match): pass    The callback receives the editable (comment, submission, message) and the matching phrase


@bot.register_regex(r'@review_bot ')
@bot.make_reply
def list_reviews(editable, match):
    pass


def _get_reviews(bottle=None, keyword=None, subreddit=None):
    ''' Get all reviews of a user.

        Args:
            bottle: (string) Get all reviews about a certain bottle.
            keyword: (string) Get all reviews matching the keyword
            subreddit: (string) Get all reviews from a certain subreddit.

        Returns:
            A generator for all reviews matching the criteria.
    '''
    pass
