# Review Bot
Review Bot is a Reddit Bot powered by PRAW (Python Reddit Api Wrapper).

The bot is not intrusive as it only replies when it is called. 
It lists up to 10 of the caller's latest reviews in the /r/Whisky network. Specific commands are listed below.

## Commands
Below are the commands Review_Bot looks for in the comments. All commands are case-insensitive.

### Generic
> @review_bot
Lists up to 10 of the user's reviews across the /r/Whisky network.

### Keyworded
> @review_bot 'Caol Ila'
> @review_bot "Caol Ila"
Lists all reviews which titles contains the phrase 'Caol Ila'.


### Per subreddit
> @review_bot scotch|bourbon|worldwhisky
Lists all reviews from just one subreddit (/r/Scotch, /r/Bourbon *or* /r/WorldWhisky)

### Combined
> @review_bot scotch|bourbon|worldwhisky 'Caol Ila'