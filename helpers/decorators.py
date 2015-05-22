import praw
import logging


def rate_limited(function):
    def wrapper(*args, **kwargs):
        while True:
            try:
                result = function(*args, **kwargs)
                break
            except praw.errors.RateLimitExceeded as error:
                logging.warning('RateLimitExceeded | Sleeping {0} seconds'.format(error.sleep_time))
                time.sleep(error.sleep_time)
        return result
    return wrapper
