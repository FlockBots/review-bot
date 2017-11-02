require 'redd'

module ReviewBot
  # include Commands

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
      inbox.each { |message| analyze message }
    end

    def analyze(message)
      @current_message = message

      commands = [recent_command, subreddit_command, whisky_command]
      commands.each do |command|
        reviews = command.match(message.body)
        build_reply(reviews)
      end

      reply(@repository.user, reviews)
    end

    def build_reply(result)
      return if result.nil?
    end

    def reply(user, reviews)
      puts user, reviews
    end

    private

    def recent_command
      prefix = "/u/#{username} latest"
      regex = /#{Regexp.quote(prefix)}/
      Command.new(regex) do
        @repository.recent_reviews
      end
    end

    def subreddit_command
      prefix = "/u/#{username} /r/"

      # command taken from reddit source: reddit/reddit: r2/models/subreddit.py
      subreddit = /[A-Za-z0-9][A-Za-z0-9_]{2,20}($|[^A-Za-z0-9_])/
      regex = /#{Regexp.quote(prefix)}(#{subreddit})/
      ParameterizedCommand.new(regex, [0]) do |subreddit|
        @repository.subreddit_reviews(subreddit)
      end
    end

    def whisky_command
      prefix = "/u/#{username}"
      regex = /#{Regexp.quote(prefix)} (["'])((?:\\\1|.)*?)\1/
      ParameterizedCommand.new(regex, [1]) do |whisky|
        whisky.delete!('\\')
        @repository.whisky_reviews(whisky)
      end
    end
  end
end
