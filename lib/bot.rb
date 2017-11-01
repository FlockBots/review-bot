require 'redd'

class Bot
  def initialize(session, review_repository)
    @session = session
    @repository = review_repository

    @limit = 10 # todo: move to config?
  end

  def username
    @session.me.name
  end

  def inbox
    session.my_messages(mark: false)
  end

  def watch_reddit
    for message in inbox do

    end
  end

  private

  def recent_command
    prefix = "/u/#{username} latest"
    regex = /#{Regexp.quote(prefix)}/
    Command.new(regex) { @repository.recent_reviews(@limit) }
  end

  def subreddit_command
    prefix = "/u/#{username} /r/"

    # command taken from reddit source: reddit/reddit: r2/models/subreddit.py
    subreddit = /^[A-Za-z0-9][A-Za-z0-9_]{2,20}$/
    regex = /#{Regexp.quote(prefix)}(#{subreddit})/
    ParameterizedCommand.new(regex, [0]) do |subreddit|
      @repository.subreddit_reviews(@limit, subreddit)
    end
  end

  def whisky_command
    prefix = "/u/#{username} "
    whisky = /#{Regexp.quote(prefix)}(["'])((?:\\\1|.)*?)\1/
    ParameterizedCommand.new(regex, [1]) do |whisky|
      @repository.whisky_reviews(@limit, whisky)
    end
  end
end
