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
      commands = [recent_command, subreddit_command, whisky_command]
      for message in inbox do
        @repository.user = message.author
        text = if message.respond_to? :selftext
                 message.selftext
               elsif message.respond_to? :body
                 message.body
               else
                 raise 'Cannot retrieve text from message.'
                 # todo: log and continue with next message
               end
        for command in commands
          reviews = command.match(text)
          next if result.nil? || result.empty?
          reply(@repository.user, reviews)
        end
      end
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
        whisky.gsub!(/\\/, '')
        @repository.whisky_reviews(whisky)
      end
    end
  end
end
