from bot import Bot
from config import info
from modules import ReviewBase
from fuzzywuzzy import fuzz
from helpers.functions import peek
from collections import namedtuple
import logging

bot = Bot.get_instance()  # Singleton
logger = logging.getLogger(__name__)

# Register function below
# @bot.make_reply                    -   Creates a reply using the returned string
# @bot.register_regex(r'my_regex')   -   Fires function if comment/submission matches regex
# def callback(editable, match): pass    The callback receives the editable (comment, submission, message) and the matching phrase


@bot.make_reply
@bot.register_regex(r'/u/review_bot list')
def list_reviews(editable, match):
    """ List reviews from a subreddit containing a certain keyword.

        Args:
            editable: The submission, message or comment containing the trigger
            match: re.Match object
        Returns: (string)
            A markdown list of matching reviews.
    """
    logger.debug('Listing reviews by {} (all)'.format(editable.author))

    reviews = _get_reviews(user=editable.author)

    if peek(reviews):
        reply = "{user}'s latest reviews:\n\n".format(user=editable.author)
        reply += _create_review_list(reviews)
    else:
        reply  = "I can't find a single review under your name. :(\n\n"
    return reply


@bot.make_reply
@bot.register_regex(r'/u/review_bot ({subs})'.format(subs='|'.join(info['review_subs'])))
def list_reviews_subreddit(editable, match):
    """ List most recent reviews from subreddit

        Args:
            editable: The submission, message or comment containing the trigger
            match: re.Match object containing the following groups:
                   1 - the name of the subreddit
        Returns: (string)
            A markdown list of matching reviews.
    """
    subreddit = match.group(1).title()
    logger.debug('Listing reviews by {} (subreddit:{})'.format(editable.author, subreddit))

    reviews = _get_reviews(user=editable.author, subreddit=subreddit)

    if peek(reviews):
        reply = "{user}'s latest reviews in /r/{sub}:\n\n".format(user=editable.author, sub=subreddit)
        reply += _create_review_list(reviews)
    else:
        reply = "You don't seem to have any reviews in /r/{sub} yet, buddy.\n\n".format(sub=subreddit)
    return reply


@bot.make_reply
@bot.register_regex(r'''/u/review_bot [`'"]([a-zA-Z0-9_\ -]+)[`'"]''')
def list_reviews_bottle(editable, match):
    """ List reviews about a certain bottle/brand.

        Args:
            editable: The submission, message or comment containing the trigger
            match: re.Match object containing the following groups:
                   1 - the name of the bottle
        Returns: (string)
            A markdown list of matching reviews.
    """
    bottle = match.group(1)
    logger.debug('Listing reviews by {} (bottle:{})'.format(editable.author, bottle))

    reviews = _get_reviews(user=editable.author, bottle=bottle)

    if peek(reviews):
        reply = "{user}'s latest `{bottle}` reviews:\n\n".format(user=editable.author, bottle=bottle)  
        reply += _create_review_list(reviews)
    else:
        reply = "Sorry, I can't seem to find any `{bottle}` reviews by you, mate. :(\n\n".format(bottle=bottle)

    return reply


ScoredReview = namedtuple('ScoredReview', ['review', 'score'])


def _get_reviews(user, subreddit=None, bottle=None):
    """ Get all reviews of a user.

        Args:
            user: (string) The username
            bottle: (string) Match criterium: reviews about bottle.
            subreddit: ([string]) Match criterium: reviews from a certain subreddit.

        Returns:
            A list for all reviews matching the criteria.
    """
    logger.debug('Getting reviews (sub:{}, bottle:{})'.format(subreddit, bottle))

    review_db = ReviewBase(info['database_filename'])
    reviews = review_db.select(author=user, subreddit=subreddit)

    if not bottle:
        return reviews

    best_matches = []

    for review in reviews:
        match_score = _calculate_match_score(review=review, bottle=bottle)
        if match_score > 66: # 2/3th of the string matches
            best_matches.append(ScoredReview(review, match_score))
    best_matches.sort(key=lambda sr: (sr.score, sr.review['date']), reverse=True)
    return (scored.review for scored in best_matches)


def _calculate_match_score(review, bottle):
    """ Calculate the ratio in which the bottle matches the review.

        Args:
            review: modules.reviewbase.Review object to match against
            string: string to match the Review with

        Returns:
            Score [0, 100], the higher the score the better the match
    """

    bottle_score = 0
    if review['bottle']:
        bottle_score = fuzz.partial_ratio(review['bottle'].lower(), bottle.lower())
        
    title_score = fuzz.partial_ratio(review['title'].lower(), bottle.lower())
    return max(bottle_score, title_score)


def _create_review_list(reviews, max_reviews=10):
    """ Create a string containing links to the reviews. """
    review_list = ''
    for index, review in reviews:
        if index >= max_reviews:
            break
        review_list += '* [{title}]({url})\n'.format(review['title'], review['permalink'])
    review_list += '\n'
    return review_list
