import re, praw, logging, requests
from Bot import Bot, Comment, Submission
import sqlite3
import classifier
from datetime import date

# specify additional database tables here
# Check Bot.py for examples
class Review():
    table = 'reviews'

    @staticmethod
    def add(submission_id, title, user, url, subreddit, date, score, db):
        cursor = db.cursor()
        try:
            cursor.execute(
                'INSERT INTO {} VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)'
                .format(Review.table),
                (submission_id, title, user, url,
                 subreddit, date, score)
            )
        except sqlite3.IntegrityError: # skip inserting this one
                logging.debug('URL already in database for this user. Skipping insertion.\n({user},{url})'.format(user=user, url=url))
        except:
            logging.exception('Unable to add review to database.')
        else:
            db.commit()

    @staticmethod
    def find(submission_id, user, db):
        cursor = db.cursor()
        try:
            cursor.execute(
                'SELECT submission_id, user FROM {} WHERE submission_id = ? AND user = ?'
                .format(Review.table), (submission_id, user)
            )
        except:
            logging.exception('Unable to perform Select query on Reviews.')
        else:
            return cursor.fetchone()

    @staticmethod
    def get(user):
        cursor = db.cursor()
        try:
            cursor.execute(
                'SELECT title, url, subreddit, score FROM {} WHERE user = ? ORDER BY date DESC'
                .format(Review.table), (user,)
            )
        except:
            logging.exception('Unable to retrieve reviews from database.')
        else:
            return cursor.fetchall()

def create_review_table(db):
    cursor = db.cursor();
    cursor.execute('''CREATE TABLE IF NOT EXISTS {} (
        id INTEGER NOT NULL,
        submission_id VARCHAR,
        title VARCHAR,
        user VARCHAR,
        url VARCHAR,
        subreddit VARCHAR,
        date INTEGER,
        score INTEGER,
        PRIMARY KEY (id)
    )'''.format(Review.table))
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS review ON {}(user, url)'.format(Review.table))
    db.commit()

class ReviewBot(Bot):
    def run(self):
        while True:
            self.loop()

    def check_comments(self, subreddit):
        logging.debug('checking latest on {0}'.format(subreddit))
        comments = self.reddit.get_comments(subreddit)
        for comment in comments:
                if not Comment.is_parsed(comment.id, self.db):
                    self.check_triggers(comment)
                    Comment.add(comment.id, self.db)
        self.idle_count += 1

    def check_submissions(self, subreddit):
        logging.debug('checking latest posts on {0}'.format(subreddit))
        submissions = self.reddit.get_subreddit(subreddit).get_new(limit=100)
        for submission in submissions:
            if not Submission.is_parsed(submission.id, self.db):
                self.check_triggers(submission)
                Submission.add(submission.id, self.db)
        self.idle_count += 1

    def check_messages(self):
        pass

    # Set certain parameters and variables for the bot
    def set_configurables(self):
        Bot.set_configurables(self)
        self.reply_header = '\n\n/u/{0}\'s {1} reviews in /r/{2}:\n\n'
        self.reply_footer = '\n\n___\n\n[^Info](http://github.com/Chronophobe/ReviewBot)^( | Please address any remarks to /u/FlockOnFire)'
        self.list_limit = 10
        self.triggers = {
            'list': re.compile(r'(@review_bot)( (scotch|bourbon|worldwhisky))?( [\`\'\"]([a-z0-9_\ -]+)[\`\'\"])?', re.I),
            'inventory': re.compile(r'@swap_bot inventory'),
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
    def check_triggers(self, post):
        body = ''
        if isinstance(post, praw.objects.Comment):
            body = post.body
        elif isinstance(post, praw.objects.Submission):
            body = post.selftext
        list_pattern = self.triggers['list']
        list_matches = list_pattern.findall(body)
        inventory_pattern = self.triggers['inventory']
        inventory_matches = list_pattern.search(body)

        reply = ''

        inventory_matches = False

        if inventory_matches:
            logging.info(inventory_matches.group(0))
            reply += self.get_inventory(post.author)
        # Matches contains tuples in the format:
        # (@review_bot list, ' network:sub', subreddit, ' keyword', keyword)
        for _, _, sub, _, keyword in list_matches:
            if not keyword:
                keyword = ''
            keywords = keyword.split()
            if not sub:
                sub = self.review_subs
            else:
                sub = [sub.lower()]

            self.add_last_reviews(post.author)
            reviews = self.get_reviews(post.author, keywords, sub)

            # list reply functions here to add a single reply
            if len(sub) == 1:
                sub = sub[0]
            reply += self.reply_header.format(post.author, keyword, sub)
            reply += self.list_reviews(reviews)
        if list_matches or inventory_matches:    
            reply += self.reply_footer
            self.reply(post, reply)
            # print(reply)
            self.idle_count = 0

    # Returns the link to the /r/WhiskyInventory submission of user
    def get_inventory(self, user):
        logging.info('Getting link to {}\'s inventory'.format(str(user)))
        link = 'No inventory found :('
        posts = user.get_submitted(limit=None)
        for post in posts:
            if post.subreddit.display_name.lower() == 'whiskyinventory':
                link = '[{user}\'s Inventory]({permalink})'.format(user=str(user), permalink=post.permalink)
                break
        return link
    # Generate a markdown list of review tuples (title, url)
    def list_reviews(self, reviews):
        text = ''
        counter = 0
        for title, url, score in reviews:
            if counter >= self.list_limit:
                break
            text += '* [{0}]({1}) - **{2}**/100\n'.format(str(title), str(url), score)
            counter += 1
        if text == '':
            text = '* Nothing here yet.\n'
        return text

    # Add the user's last reviews to the database
    def add_last_reviews(self, redditor):
        logging.info('Adding {}\'s reviews to the database'.format(str(redditor)))
        posts = redditor.get_submitted(limit=None, sort = 'new')
        for post in posts:
            if Review.find(post.id, str(redditor).lower(), self.db):
                break
            post = self.reddit.get_submission(submission_id = post.id, comment_sort = 'old')
            review_comment = self.submission_is_review(submission = post)
            if review_comment:
                logging.info('Found review: {}'.format(review_comment.permalink))
                review_date = date.fromtimestamp(review_comment.created_utc)
                try:
                     score = int(self.get_score(comment = review_comment))
                except:
                    logging.debug('   Warning: no score')
                    score = None
                Review.add(
                    submission_id = post.id,
                    title = bytes(post.title, 'utf-8'),
                    user = str(post.author).lower(),
                    url = post.permalink,
                    subreddit = post.subreddit.display_name.lower(),
                    date = review_date.strftime('%Y%m%d'),
                    score = score,
                    db = self.db 
                )
                logging.debug('Adding review ({}) to database.'.format(post.id))

    # returns a generator with all matching reviews
    def get_reviews(self, redditor, keywords = [], sub = None):
        logging.info('Getting {}\'s {} reviews'.format(str(redditor), keywords))
        if not sub:
            sub = self.review_subs
        reviews = Review.get(str(redditor).lower())
        for title, url, subreddit, score in reviews:
            logging.debug(title)
            title = str(title.decode('utf-8'))
            lower_title = title.lower()
            if subreddit in sub \
            and all([keyword.lower() in lower_title for keyword in keywords]):
                if not score:
                    score = '??'
                yield (title, url, score)

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
                    if self.get_comment_class(comment = comment) == 1 and \
                    comment.author == submission.author and len(comment.body) > 200:
                        logging.debug('        contains a review')
                        return comment
                except requests.exceptions.HTTPError as e:
                    logging.warning(e)
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
        pattern = re.compile(r'(\d+)[*]* ?\/ ?100')
        score = pattern.search(text)
        if score:
            return score.group(1)
        return ''

    # Reply - separate function for debugging purposes.
    def reply(self, post, text):
        if isinstance(post, praw.objects.Comment):
            Bot.handle_ratelimit(post.reply, text)
        elif isinstance(post, praw.objects.Submission):
            Bot.handle_ratelimit(post.add_comment, text)

with sqlite3.connect('bot.db') as db:
    create_review_table(db)
    review_bot = ReviewBot('Review_Bot 2.2 by /u/FlockOnFire', 'review.log', from_file='login.cred', database=db)
    review_bot.run()
