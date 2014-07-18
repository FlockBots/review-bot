import re, praw, logging, requests
from Bot import Bot, Comment, Database
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import desc
import classifier
from datetime import date

# specify additional database tables here
# Check Bot.py for examples

class Review(Database.Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    submission_id = Column(String)
    title = Column(String)
    user = Column(String)
    url = Column(String)
    subreddit = Column(String)
    date = Column(Integer)
    score = Column(Integer, nullable=True)

    def __init__(self, submission_id, title, user, url, subreddit, date, score):
        self.submission_id = submission_id
        self.title = title
        self.user = user
        self.url = url
        self.subreddit = subreddit
        self.date = date
        self.score = score

    def add(self, session):
        session.add(self)
        session.commit()

db = Database()

class ReviewBot(Bot):
    def run(self):
        while True:
            self.loop()

    def check_comments(self, subreddit):
        logging.debug('checking latest on {0}'.format(subreddit))
        comments = self.reddit.get_comments(subreddit)
        for comment in comments:
                if not Comment.is_parsed(comment.id):
                    self.check_triggers(comment)
                    Comment.add(comment.id, self.db.session)
        self.idle_count += 1

    def check_messages(self):
        pass

    # Set certain parameters and variables for the bot
    def set_configurables(self):
        Bot.set_configurables(self)
        self.reply_header = '\n\n/u/{0}\'s {1} reviews in /r/{2}:\n\n'
        self.reply_footer = '\n\n___\n\n^(Please report any issues to /u/FlockOnFire)'
        self.list_limit = 10
        self.triggers = {
            '@review_bot': re.compile(r'(@review_bot)( (scotch|bourbon|worldwhisky))?( [\'|\"]([a-z0-9_\ -]+)[\'\"])?', re.I),
        }
        self.sub_from_subscriptions = True 
        self.review_subs = ['scotch', 'bourbon', 'worldwhisky']
        print("""
            List limit:          {0}
        """.format(self.list_limit))

    def set_properties(self):
        Bot.set_properties(self)
        self.refresh_cap = 30

    # Check comment for triggers
    def check_triggers(self, comment):
        pattern = self.triggers['@review_bot']
        matches = pattern.findall(comment.body)

        # Matches contains tuples in the format:
        # (@review_bot, ' network:sub', subreddit, ' keyword', keyword)
        reply = ''
        for _, _, sub, _, keyword in matches:
            if not keyword:
                keyword = ''
            keywords = keyword.split()
            if not sub:
                sub = self.review_subs
            else:
                sub = [sub.lower()]

            self.add_last_reviews(comment.author)
            reviews = self.get_reviews(comment.author, keywords, sub)

            # list reply functions here to add a single reply
            if len(sub) == 1:
                sub = sub[0]
            reply += self.reply_header.format(comment.author, keyword, sub)
            reply += self.list_reviews(reviews)
        if matches:    
            reply += self.reply_footer
            self.reply(comment, reply)
            self.idle_count = 0

    # Generate a markdown list of review tuples (title, url)
    def list_reviews(self, reviews):
        text = ''
        listed = []
        counter = 0
        for subm_id, title, url, score in reviews:
            if counter >= self.list_limit:
                break
            if subm_id in listed:
                continue
            text += '* [{0}]({1}) - **{2}**/100\n'.format(str(title), str(url), score)
            counter += 1
            listed.append(subm_id)
        if text == '':
            text = '* Nothing here yet.\n'
        return text

    # Add the user's last reviews to the database
    def add_last_reviews(self, redditor):
        logging.debug('Adding {}\'s reviews to the database'.format(str(redditor)))
        posts = redditor.get_submitted(limit=None, sort='top')
        for post in posts:
            if Review.query.filter(Review.submission_id == post.id).first():
                break
            review_comment = self.submission_is_review(submission = post)
            if review_comment:
                review_date = date.fromtimestamp(review_comment.created_utc)
                try:
                     score = int(self.get_score(comment = review_comment))
                except:
                    logging.debug('   Warning: no score')
                    score = None
                review = Review(
                    submission_id = post.id,
                    title = bytes(post.title, 'utf-8'),
                    user = str(post.author).lower(),
                    url = post.permalink,
                    subreddit = post.subreddit.display_name.lower(),
                    date = review_date.strftime('%Y%m%d'),
                    score = score 
                )
                review.add(self.db.session)
                logging.debug('Adding review ({}) to database.'.format(review.submission_id))

    # returns a generator with all matching reviews
    def get_reviews(self, redditor, keywords = [], sub = None):
        logging.info('Getting {}\'s {} reviews'.format(str(redditor), keywords))
        if not sub:
            sub = self.review_subs
        reviews = Review.query.filter(Review.user == str(redditor).lower()).order_by(desc(Review.date)).all()
        for review in reviews:
            logging.debug(review.title)
            title = str(review.title.decode('utf-8'))
            lower_title = title.lower()
            if review.subreddit in sub \
            and all([keyword.lower() in lower_title for keyword in keywords]):
                if not review.score:
                    review.score = '??'
                yield (review.submission_id, title, review.url, review.score)

    # Check if user's submission is a review
    def submission_is_review(self, submission):
        logging.debug('Checking Submission({})'.format(submission.id))
        title = not submission.is_self \
        and submission.subreddit.display_name.lower() in self.review_subs
        if title:
            logging.debug('    properties check out')
            submission.replace_more_comments(limit=None, threshold=0)
            comments = praw.helpers.flatten_tree(submission.comments)
            for comment in comments:
                try:
                    logging.debug('    {}'.format(comment.permalink))
                    if self.get_comment_class(comment = comment) == 1 and comment.author == submission.author:
                        logging.debug('        contains a review')
                        return comment
                except requests.exceptions.HTTPError as e:
                    logging.warning(Bot.get_time() + '    {0}'.format(e))
                    continue
        logging.debug('    not a review')
        return None

    # Get comment class
    # Returns 1 if comment is a review
    # Returns -1 if comment is not a review
    def get_comment_class(self, text = None, comment = None):
        if comment:
            text = comment.body
        classifier.vectorizer.input = 'content'
        X_test = classifier.vectorizer.transform([text])
        classifier.vectorizer.input = 'filename' # undo side-effect
        return classifier.clf.predict(X_test)[0]

    # Get the score out of a comment
    def get_score(self, text = None, comment = None):
        if comment:
            text = comment.body
        pattern = re.compile(r'[*]*(\d+)[*]* ?\/ ?100')
        score = pattern.search(text)
        if score:
            return score.group(1)
        return ''

    # Reply - separate function for debugging purposes.
    def reply(self, comment, text):
        Bot.handle_ratelimit(comment.reply, text)
        # print('{}\n{}'.format(str(comment.author), text.encode('utf-8')))
        # print()

review_bot = ReviewBot('Review_Bot 2.2 by /u/FlockOnFire', 'review.log', from_file='login.cred', database=db)
review_bot.run()
