from bot import Bot

bot = Bot()  # Singleton, requires to be initialised before

# Register function below
# @bot.register_regex(r'my_regex')   -   Fires function if comment/submission matches regex
# @bot.make_reply                    -   Creates a reply using the returned string
# def callback(editable, match): pass    The callback receives the editable (comment, submission, message) and the matching phrase


@bot.register_regex(r'''(/u/review_bot list)( (scotch|bourbon|worldwhisky))?( [`'"]([a-z0-9_\ -]+)[`'"])?''')
@bot.make_reply
def list_reviews(editable, match):
    ''' List reviews from a subreddit containing a certain keyword.

        Args:
            editable: The submission, message or comment containing the trigger
            match: re.Match object containing the following groups:
                3: the subreddit
                5: the keyword
        Returns: (string)
            A markdown list of matching reviews. 
    '''
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
