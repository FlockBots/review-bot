require 'redd'

module ReviewBot
  class Bot
    include Commands

    def initialize(session, review_repository, logger)
      @session = session
      @repository = review_repository
      @logger = logger
    end

    def username
      @session.me.name
    end

    def inbox
      options = { category: 'unread', mark: false }.freeze
      Redd::Models::PaginatedListing.new(@session.client, options) do |**req_options|
        @session.my_messages(options.merge(req_options))
      end.stream
    end

    def watch_reddit
      inbox do |message|
        text = analyze(message)
        message.reply(text + footer) unless text.empty?
        message.mark_as_read
      end
    end

    def analyze(comment)
      username = comment.author.name
      commands = [recent_command, subreddit_command, whisky_command]

      commands.map do |command|
        text = comment.body
        results = command.match(text, username)
        results.map {|result| build_reply(result, username)}
      end.flatten.join("\n")
    end

    def build_reply(result, username)
      return '' if result.return_value.nil?
      reply_body = header(username, arguments)
      reviews = reviews_list(result.return_value) || "_No results._"
      reply_body + "\n\n"
    end

    private

    def footer
      "___\n"\
        "^(More info? Ask /u/FlockOnFire or click )"\
        "^[here](https://github.com/FlockBots/review-bot)."
    end

    def header(username, arguments)
      args = arguments.clone.shift # shift off bot's username
      reply_body = "/u/#{username}'s latest reviews"
      reply_body << " (#{args.first})" unless args.empty?
      reply_body << "\n\n"
    end

    def reviews_list(reviews)
      reviews.map do |review|
        "* #{review.rating_string}/100 - [#{review.whisky}](#{review.url})"
      end.join("\n")
    end

    def prefix
      "/u/#{username}"
    end

    def recent_command
      regex = /#{Regexp.quote(prefix)} (latest)/i
      ParameterizedCommand.new(regex) do |username|
        @repository.recent_reviews(username)
      end
    end

    def subreddit_command
      # regex taken from reddit source: reddit/reddit: r2/models/subreddit.py
      subreddit = /[a-z0-9][a-z0-9_]{2,20}/
      regex = /#{Regexp.quote(prefix)} \/r\/(#{subreddit})($|[^a-z0-9_])/i
      ParameterizedCommand.new(regex, [0]) do |username, sub|
        @repository.subreddit_reviews(username, sub)
      end
    end

    def whisky_command
      regex = /#{Regexp.quote(prefix)} (["'])((?:\\\1|.)*?)\1/i
      ParameterizedCommand.new(regex, [1]) do |username, whisky|
        whisky.delete!('\\')
        @repository.whisky_reviews(username, whisky)
      end
    end
  end
end
