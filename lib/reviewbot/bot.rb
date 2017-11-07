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
      end.stream do |comment|
        yield comment
      end
      raise 'Unexpected end of stream'
    end

    def watch_reddit
      inbox do |message|
        text = analyze message
        reply(text + footer, message) unless text.empty?
        message.mark_as_read
      end
    end

    def analyze(message)
      username = message.author.name
      @logger.debug("[#{message.id}]\tAnalyzing")
      commands = [recent_command, subreddit_command, whisky_command]
      commands.map do |command|
        text = get_text(message)
        results = command.match(text, username)
        unless results.empty?
          @logger.debug("Results: #{results}")
          results.map {|result| build_reply(result, message.author.name)}
        end
      end.flatten.reject(&:nil?).join("\n")
    end

    def build_reply(result, username)
      return '' if result.return_value.nil?
      reply_body = "/u/#{username}'s latest reviews"
      arguments = result.arguments.clone
      arguments.shift # shift off username -- TODO: Too coupled
      reply_body += " (#{arguments.first})" unless arguments.empty?
      reply_body += "\n\n"
      @logger.debug(result.return_value.count)
      result.return_value.each do |review|
        rating = review.rating.nil? ? '--' : review.rating
        reply_body += "* (#{review.rating}/100) [#{review.whisky}](#{review.url})\n"
      end
      if result.return_value.empty?
        reply_body += "_No results._\n"
      end
      reply_body + "\n"
    end

    def reply(text, message)
      return if text.empty?
      @logger.info("[#{message.id}]\tReplying to #{message.author.name}")
      message.reply(text)
    end

    private

    def footer
      "___\n"\
        "^(More info? Ask /u/FlockOnFire or click )"\
        "^[here](https://github.com/FlockBots/review-bot)."
    end

    def get_text(message)
      if message.respond_to? :body
        message.body
      elsif message.respond_to? :selftext
        message.selftext
      else
        raise 'Cannot retrieve text from message.'
      end
    end

    def recent_command
      prefix = "/u/#{username}"
      regex = /#{Regexp.quote(prefix)} (latest)/i
      ParameterizedCommand.new(regex) do |username|
        @repository.recent_reviews(username)
      end
    end

    def subreddit_command
      prefix = "/u/#{username} /r/"

      # command taken from reddit source: reddit/reddit: r2/models/subreddit.py
      subreddit = /[a-z0-9][a-z0-9_]{2,20}/
      regex = /#{Regexp.quote(prefix)}(#{subreddit})($|[^a-z0-9_])/i
      ParameterizedCommand.new(regex, [0]) do |username, sub|
        @repository.subreddit_reviews(username, sub)
      end
    end

    def whisky_command
      prefix = "/u/#{username}"
      regex = /#{Regexp.quote(prefix)} (["'])((?:\\\1|.)*?)\1/i
      ParameterizedCommand.new(regex, [1]) do |username, whisky|
        whisky.delete!('\\')
        @repository.whisky_reviews(username, whisky)
      end
    end
  end
end
