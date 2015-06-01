import praw
import logging


def rate_limited(function):
    ''' Tries to execute a Reddit API related function. 
        If the Reddit rate limit is exceeded, it sleeps for a sufficient amount of time before retrying.
    '''
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


def cursor_op(function):
    ''' Opens the cursor, passes it to the function and closes it.
        Requires a instance variable named 'connection' of type sqlite3.Connection.
        Decorated function should accept an argument called cursor.
    '''
    def wrapper(*args, **kwargs):
        cursor = self.connection.cursor()
        result = function(*args, cursor=cursor, **kwargs)
        cursor.close()
        return result
    return wrapper
