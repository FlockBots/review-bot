from helpers import Editable
from modules import classifier
from modules import ReviewBase
from helpers.bot import Callback
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
            regex=r'',
            function=functools.partial(classify_editable, review_db=review_db)
        )
    ]


def classify_editable(editable, match):
    """ Check whether the comment or submission is a review or not and
        add it to the database.

        Args:
            editable: The submission, message or comment containing the trigger
            match: re.Match object. Irrelevant here.
        Returns:
            None
    """
    classifier = Classifier(database_file='data/classified_reviews')

    # Only comments and submissions can be reviews
    if editable.type not in [Editable.Comment, Editable.Submission]:
        return

    # if it is a review, then add it to the database.
    if classifier.classify(editable.text):
        logger.info('Classified review: {}'
                    .format(editable.permalink))
        review = {
            'author': editable.author,
            'bottle': '',
            'date': editable.date.strftime('%Y%m%d'),
            'permalink': editable.permalink,
            'score': _get_score(editable.text),
            'subreddit': editable.subreddit,
            'title': editable.submission.title
        }
        ReviewBase().insert(review)


def _get_score(text):
    """ Extracts the score from the text. Returns the first match.

        Args:
            text: (string) Text to search through to find a score.
        Returns:
            Integer between 0 and 100 if a score is found
            None otherwise
    """

    # Search for the default xx/100 format (decimals up to two places allowed)
    out_of_hundred = re.findall(r'(\d{1,3})(?:[\.,]\d{1,2})?/100', text)
    if out_of_hundred:
        return int(out_of_hundred[0])

    # Search for the xx/10 format (decimals up to two places allowed)
    out_of_ten = re.findall(r'(\d{1,2})(?:[\.,]\d{1,2})?/10', text)
    if out_of_ten:
        return int(out_of_ten[0])

    # Grab any digit between 1 and 100, return the last
    other = re.findall(r'(\d{1,3})', text)
    if other:
        return int(other[-1])

    return None
