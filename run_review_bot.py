import re, praw, logging, requests
from Bot import Bot, Comment, Database

db = Database()

class ReviewBot(Bot):
    def run(self):
        while True:
            self.loop()

    # Check the latest hot submissions in subreddit
    def check_submissions(self, subreddit):
        subreddit = self.reddit.get_subreddit(subreddit)
        for submission in subreddit.get_hot(limit=20):
            submission.replace_more_comments(limit=None, threshold=0)
            comments = praw.helpers.flatten_tree(submission.comments)
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
        self.reply_header = '{0}\'s {1} reviews in {2}:\n\n'
        self.reply_footer = '\n___\n^(Please report any issues to /u/FlockOnFire)\n\n'
        self.list_limit = 10
        self.triggers = {
        #(@reviewbot)( [\'|\"]([a-z0-9_\ -]+)[\'\"])?( network:(scotch|bourbon|worldwhisky))?
            '@review_bot': re.compile(r'(@review_bot)( [\'|\"]([a-z0-9_\ -]+)[\'\"])?( network:(scotch|bourbon|worldwhisky))?', re.I),
        }
        self.subreddits = ['FlockBots']
        # self.subreddits = [sub.display_name for sub in self.reddit.get_my_subreddits()]
        self.review_subs = ['scotch', 'bourbon', 'worldwhisky']
        print("""
            Subreddits:          {0}
            List limit:          {1}
        """.format(self.subreddits, self.list_limit))

    # Check comment for triggers
    def check_triggers(self, comment):
        pattern = self.triggers['@review_bot']
        matches = pattern.findall(comment.body)

        # Matches contains tuples in the format:
        # (@review_bot, ' keyword', keyword, ' network:sub', subreddit)
        reply = ''
        for _, _, keyword, _, sub in matches:
            if not keyword:
                keyword = ''
                keywords = ['']
            if not sub:
                sub = self.review_subs
            else:
                sub = [sub]
            # list reply functions here to add a single reply
            reply += self.reply_header.format(comment.author, keyword, sub)
            reviews = self.get_last_reviews(comment.author, keywords, sub)
            reply += self.list_reviews(reviews)
            
        reply += self.reply_footer
        Bot.handle_ratelimit(comment.reply, reply)
        self.idle_count = 0

    # Generate a markdown list of review tuples (title, url)
    def list_reviews(self, reviews):
        if len(reviews) == 0:
            return 'No reviews yet!'
        else:
            text = ''
            for title, url in reviews:
                text += "* [{0}]({1})\n".format(title, url)
            return text

    # Get the Redditor's last reviews in Sub containing Keywords in the title
    def get_last_reviews(self, redditor, keywords, sub):
        logging.info(Bot.get_time() + '    Listing Reviews: {0}'.format(str(redditor)))
        counter = 0
        author_posts = redditor.get_submitted(limit=None)
        last_reviews = []
        print(self.list_limit)
        for post in author_posts:
            if counter < self.list_limit and self.submission_is_review(post, keywords, sub):
                last_reviews.append((post.title, post.permalink))
                counter += 1
                print(str(counter))
        return last_reviews

    # Check if user's submission is a review
    def submission_is_review(self, submission, keywords, sub):
        keywords.append('review')
        title = not submission.is_self \
        and submission.subreddit.display_name.lower() in sub \
        and all(keyword in submission.title.lower() for keyword in keywords)
        if title:
            print(Bot.get_time() + ": " + submission.title)
            submission.replace_more_comments(limit=None, threshold=0)
            comments = praw.helpers.flatten_tree(submission.comments)
            for comment in comments:
                try:
                    if self.comment_is_review(comment, submission.author):
                        return True
                except requests.exceptions.HTTPError as e:
                    logging.warning(Bot.get_time() + '    {0}'.format(e))
                    continue
        return False

    # Check if the comment is part of the review
    def comment_is_review(self, comment, author):
        if comment.author != author:
            return False
        return all(string in comment.body.lower() for string in ['finish', 'nose'])

review_bot = ReviewBot('Review_Bot 2.0 by /u/FlockOnFire', 'review.log', from_file='login.cred', database=db)
review_bot.run()