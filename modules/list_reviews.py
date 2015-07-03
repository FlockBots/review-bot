from helpers.bot import Callback
from config import info
from modules import ReviewBase
from fuzzywuzzy import fuzz
from helpers.functions import peek
from collections import namedtuple
import logging
import functools


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

def register(review_db):
    """ Returns a list of tuples containing regular expressions and
        their callback functions

        Args:
            review_db: instance of ReviewBase. Required to insert new reviews.
        Returns:
            A list of Callback tuples (regex and function pairs)
    """
    return [
        Callback(
         regex=r'(/u/{username} list)'.format(
            username=info['username']),
         function=functools.partial(list_reviews,
            review_db=review_db)
         ),

        Callback(
         regex=r'/u/{username} ({subs})'.format(
            username=info['username'],
            subs='|'.join(info['review_subs'])),
         function=functools.partial(list_reviews_subreddit,
            review_db=review_db)
         ),

        Callback(
         regex='''/u/{username} [`'"]([a-zA-Z0-9_\ -]+)[`'"]'''.format(
            username=info['username']),
         function=functools.partial(list_reviews_bottle,
            review_db=review_db)
         ),
    ]


def list_reviews(editable, match, review_db):
    """ List reviews from a subreddit containing a certain keyword.

        Args:
            editable: The submission, message or comment containing the trigger
            match: list of matches (irrelevant to this function)
        Returns: (string)
            A markdown list of matching reviews.
    """
    logger.debug('Listing reviews by {} (all)'.format(editable.author.name))

    reviews = _get_reviews(user=editable.author.name, review_db=review_db)

    peek_review, reviews = peek(reviews)
    if peek_review:
        reply = "{user}'s latest reviews:\n\n".format(user=editable.author.name)
        reply += _create_review_list(reviews)
    else:
        reply = "I can't find a single review under your name. :(\n\n"
    return reply


def list_reviews_subreddit(editable, match, review_db):
    """ List most recent reviews from subreddit

        Args:
            editable: The submission, message or comment containing the trigger
            match: list of subreddits
        Returns: (string)
            A markdown list of matching reviews.
    """

    logger.debug('Listing reviews by {} (subreddit:{})'.format(editable.author.name, match))

    reply = ''
    for subreddit in match:
        reviews = _get_reviews(
            user=editable.author.name, review_db=review_db, subreddit=subreddit)

        peek_review, reviews = peek(reviews)
        if peek_review:
            reply += "{user}'s latest reviews in /r/{sub}:\n\n".format(
                user=editable.author.name, sub=subreddit)
            reply += _create_review_list(reviews)
        else:
            reply += "You don't seem to have any reviews in /r/{sub} yet, buddy.\n\n".format(sub=subreddit)
    return reply


def list_reviews_bottle(editable, match, review_db):
    """ List reviews about a certain bottle/brand.

        Args:
            editable: The submission, message or comment containing the trigger
            match: List of all bottles
        Returns: (string)
            A markdown list of matching reviews.
    """
    logger.debug('Listing reviews by {} (bottle:{})'.format(
        editable.author.name, match))

    reply = ''
    for bottle in match:
        reviews = _get_reviews(
            user=editable.author.name, review_db=review_db, bottle=bottle)
        peek_review, reviews = peek(reviews)
        if peek_review:
            reply += "{user}'s latest `{bottle}` reviews:\n\n".format(
                user=editable.author.name, bottle=bottle)
            reply += _create_review_list(reviews)
        else:
            reply += "Sorry, I can't seem to find any `{bottle}` reviews by you, mate. :(\n\n".format(bottle=bottle)
    return reply


ScoredReview = namedtuple('ScoredReview', ['review', 'score'])


def _get_reviews(user, review_db, subreddit=None, bottle=None):
    """ Get all reviews of a user.

        Args:
            user: (string) The username
            bottle: (string) Match criterium: reviews about bottle.
            subreddit: ([string]) Match criterium: reviews from a certain subreddit.

        Returns:
            A list for all reviews matching the criteria.
    """
    logger.debug('Getting reviews (sub:{}, bottle:{})'.format(subreddit, bottle))
    user = user.lower()
    if subreddit:
        subreddit = subreddit.lower()
    reviews = review_db.select(author=user, subreddit=subreddit)

    if not bottle:
        return reviews

    best_matches = []

    for review in reviews:
        match_score = _calculate_match_score(review=review, bottle=bottle)
        if match_score > 66:  # 2/3th of the string matches
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
    for index, review in enumerate(reviews):
        if index >= max_reviews:
            break
        review_list += '* [{title}]({url})\n'.format(
            title=review['title'], url=review['permalink']
        )
    review_list += '\n'
    return review_list
