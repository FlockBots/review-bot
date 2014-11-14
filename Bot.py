# Python Bot Helper class by /u/FlockOnFire
import praw, time, logging, requests, sys, math, sqlite3

class Bot:
    def __init__(self, name, log_file, username = None, password = None, from_file = None, database = None):
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format = '{asctime} | {levelname:^8} | {message}',
            style='{'
        )
        logging.getLogger().addHandler(logging.StreamHandler())
        requests_logger = logging.getLogger('requests')
        requests_logger.setLevel(logging.WARNING)

        self.name = name
        self.db = database
        if self.db:
            self.prepare_database()

        if from_file:
            self.reddit = self.login(from_file = from_file)
        else:
            self.reddit = self.login(username, password)

        self.set_properties()
        self.set_configurables()
        
        init_msg = """
        Starting {0}...
            Username:            {1}
            Refresh rate:        {2}
            Refresh rate cap:    {3}
        """.format(self.name, str(self.reddit.user), self.refresh_rate, self.refresh_cap)
        print(init_msg)

    def set_configurables(self):
        self.refresh_rate = 10
        self.refresh_cap  = 120
        self.sub_from_subscriptions = False

    def prepare_database(self):
        cursor = self.db.cursor()
        query = 'CREATE TABLE IF NOT EXISTS {} ({})'
        cursor.execute(query.format(Comment.table, 'id VARCHAT NOT NULL'))
        cursor.execute(query.format(Submission.table, 'id VARCHAT NOT NULL'))
        self.db.commit()
        pass

    def login(self, username = None, password = None, from_file = None):
        reddit = praw.Reddit('User-Agent: {0}'.format(self.name))
        if from_file:
            with open(from_file, 'r') as f:
                credentials = f.read().splitlines()
                username = credentials[0]
                password = credentials[1]

        if username and password:
            reddit.login(credentials[0], credentials[1])
        else:
            reddit.login()
        return reddit

    def check_submissions(self, subreddit):
        pass

    def check_comments(self, subreddit):
        pass
        
    def check_messages(self):
        pass

    def loop(self):
        try:
            if self.sub_from_subscriptions:
                self.subreddits = [sub.display_name for sub in self.reddit.get_my_subreddits()]
            else:
                self.subreddits = ['FlockBots']
            for sub in self.subreddits:
                self.check_comments(sub)
                self.check_submissions(sub)
            self.check_messages()
            time.sleep(Bot.sleep_time(self.idle_count, self.refresh_rate, self.refresh_cap))
            self.http_error_count = 0
        except requests.exceptions.HTTPError as e:
            self.http_error_count += 1
            if self.http_error_count > 5:
                log.error('No connection available.')
                raise EnvironmentError('No connection available.')
            else:
                time.sleep(150)
        except Exception as e:
            logging.exception('Terminating due to error')

    def set_properties(self):
        self.idle_count = 0
        self.http_error_count = 0

    @staticmethod
    def sleep_time(n, y_min, y_max, speed = 3):
        x     = min(180, n * speed)
        angle = math.radians(x)
        y     = (-math.cos(x) * (y_max - y_min) / 2) + (y_max + y_min) / 2
        return int(y)

    @staticmethod
    def handle_ratelimit(func, *args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
                break
            except praw.errors.RateLimitExceeded as error:
                logging.warning('RateLimitExceeded | Sleeping {0} seconds'.format(error.sleep_time))
                time.sleep(error.sleep_time)

class Comment():
    table = 'comments'

    @staticmethod
    def add(comment_id, db):
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO {} VALUES (?)'.format(Comment.table), (comment_id,))
        except:
            logging.exception('Could not add comment to database.')
        else:
            db.commit()

    @staticmethod
    def is_parsed(comment_id, db):
        cursor = db.cursor()
        try:
            cursor.execute('SELECT id FROM {} WHERE id = ?'.format(Comment.table), (comment_id,))
        except:
            logging.exception('Could not perform a SELECT query on Comments')
        else:
            return cursor.fetchone()

class Submission():
    table = 'submissions'

    @staticmethod
    def add(submission_id, db):
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO {} VALUES (?)'.format(Comment.table), (submission_id,))
        except:
            logging.exception('Could not add submission to database.')
        else:
            db.commit()

    @staticmethod
    def is_parsed(submission_id, db):
        cursor = db.cursor()
        try:
            cursor.execute('SELECT id FROM {} WHERE id = ?'.format(Comment.table), (submission_id,))
        except:
            logging.exception('Could not perform a SELECT query on Submissions')
        else:
            return cursor.fetchone()
