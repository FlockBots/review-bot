# Python Bot Helper class by /u/FlockOnFire
import praw, time, logging, requests, sys, math

class Bot:
    def __init__(self, name, log_file, username = None, password = None, from_file = None, database = None):
        logging.basicConfig(filename=log_file, level=logging.INFO)
        self.name = name
        self.db = database
        if from_file:
            self.reddit = self.login(from_file = from_file)
        else:
            self.reddit = self.login(username, password)

        self.set_configurables()
        self.set_properties()

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

    def check_messages(self):
        pass

    def loop(self):
        try:
            for sub in self.subreddits:
                self.check_submissions(sub)
            self.check_messages()
            time.sleep(Bot.sleep_time(self.idle_count, self.refresh_rate, self.refresh_cap))
        except requests.exceptions.HTTPError as e:
            self.http_error_count += 1
            if self.http_error_count > 5:
                raise EnvironmentError('No connection available.')
            else:
                time.sleep(150)

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
    def get_time():
        return time.strftime("%d-%m-%Y %H:%M:%S")

    @staticmethod
    def handle_ratelimit(func, *args, **kwargs):
        while True:
            try:
                func(*args, **kwargs)
                break
            except praw.errors.RateLimitExceeded as error:
                logging.warning('RateLimitExceeded | Sleeping {0} seconds'.format(error.sleep_time))
                time.sleep(error.sleep_time)

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class Database():
    Base = declarative_base()
    def __init__(self, file = 'bot.db'):
        self.engine = create_engine('sqlite:///' + file, convert_unicode=True)
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                 autoflush=False,
                                                 bind=self.engine))
        self.Base.query = self.session.query_property()
        self.Base.metadata.create_all(bind=self.engine)

class Comment(Database.Base):
    __tablename__ = 'comments'
    id = Column(String, primary_key=True)

    def __init__(self, comment_id):
        self.id = comment_id

    @staticmethod
    def add(comment_id, session):
        session.add(Comment(comment_id))
        session.commit()

    @staticmethod
    def is_parsed(comment_id):
        return Comment.query.filter(Comment.id == comment_id).count() > 0

    @staticmethod
    def find(id):
        return Comment.query.filter(Comment.id == id).first()