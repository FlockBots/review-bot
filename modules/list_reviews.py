from bot import Callback
from config import info
from config import credentials
from modules import ReviewBase
from fuzzywuzzy import fuzz
from helpers.functions import peek
from collections import namedtuple
import logging
import functools


logger = logging.getLogger(__name__)

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
         regex=r'{username} list'.format(
            username=credentials['username']),
         function=functools.partial(list_reviews,
            review_db=review_db)
         ),

        Callback(
         regex=r'{username} ({subs})'.format(
            username=credentials['username'],
            subs='|'.join(info['review_subs'])),
         function=functools.partial(list_reviews_subreddit,
            review_db=review_db)
         ),

        Callback(
         regex='''{username} [`'"]([a-zA-Z0-9_\ -]+)[`'"]'''.format(
            username=credentials['username']),
         function=functools.partial(list_reviews_bottle,
            review_db=review_db)
         ),
    ]


def list_reviews(editable, match, review_db):
    """ List reviews from a subreddit containing a certain keyword.

        Args:
            editable: The submission, message or comment containing the trigger
            match: re.Match object
        Returns: (string)
            A markdown list of matching reviews.
    """
    logger.debug('Listing reviews by {} (all)'.format(editable.author))

    reviews = _get_reviews(user=editable.author, review_db=review_db)

    if peek(reviews):
        reply = "{user}'s latest reviews:\n\n".format(user=editable.author)
        reply += _create_review_list(reviews)
    else:
        reply = "I can't find a single review under your name. :(\n\n"
    return reply


def list_reviews_subreddit(editable, match, review_db):
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

    reviews = _get_reviews(user=editable.author, review_db=review_db, subreddit=subreddit)

    if peek(reviews):
        reply = "{user}'s latest reviews in /r/{sub}:\n\n".format(user=editable.author, sub=subreddit)
        reply += _create_review_list(reviews)
    else:
        reply = "You don't seem to have any reviews in /r/{sub} yet, buddy.\n\n".format(sub=subreddit)
    return reply


def list_reviews_bottle(editable, match, review_db):
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

    reviews = _get_reviews(user=editable.author, review_db=review_db, bottle=bottle)

    if peek(reviews):
        reply = "{user}'s latest `{bottle}` reviews:\n\n".format(user=editable.author, bottle=bottle)  
        reply += _create_review_list(reviews)
    else:
        reply = "Sorry, I can't seem to find any `{bottle}` reviews by you, mate. :(\n\n".format(bottle=bottle)

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

    reviews = review_db.select(author=user, review_db=review_db, subreddit=subreddit)

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
    for index, review in reviews:
        if index >= max_reviews:
            break
        review_list += '* [{title}]({url})\n'.format(
            title=review['title'], url=review['permalink']
        )
    review_list += '\n'
    return review_list
