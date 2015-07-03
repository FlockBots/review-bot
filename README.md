# Review Bot
Review Bot is a Reddit Bot powered by PRAW (Python Reddit Api Wrapper).

The bot is not intrusive as it only replies when it is called. 
It lists up to 10 of the caller's latest reviews in the /r/Whisky network. Specific commands are listed below.

## Commands
Below are the commands Review_Bot looks for in the comments. All commands are case-insensitive.

### Generic Listing
    /u/review_bot list

Lists up to 10 of the user's reviews across the /r/Whisky network.

### Keyworded Listing
    /u/review_bot 'Caol Ila'
    /u/review_bot "Caol Ila"
    /u/review_bot `Caol Ila`


Lists up to 10 of the user's reviews which titles contain the phrase 'Caol Ila' or the bottle information in the archive contains this phrase.  

The search is approximate, so a small typo won't matter. It lists all results that match to a certain extend which might actually be inaccurate at times where there is no real match available.

### Per subreddit Listing
    /u/review_bot scotch
    /u/review_bot bourbon
    /u/review_bot worldwhisky

Lists up to 10 of the user's reviews from just one subreddit (/r/Scotch, /r/Bourbon *or* /r/WorldWhisky)

## Running ReviewBot yourself
The bare bot (app.py + helpers/bot.py) is pretty simple and only relies on praw as external library.

Most of the configuration can be done via the `config.template/` directory. Rename it to `config` and fill in the values.

In order to classify whisky reviews from /r/scotch, /r/bourbon and /r/worldwhisky the bot uses scikit-learn. 
A database of approximately 13000 samples is provided to train your classifier.

If you want to create your own bot take a look at [FlockBots/BotBase](https://github.com/FlockBots/BotBase)