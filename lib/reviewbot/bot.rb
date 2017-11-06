require 'redd'

module ReviewBot
  class Bot
    include Commands

    def initialize(session, review_repository)
      @session = session
      @repository = review_repository

      @limit = 10 # todo: move to config?
    end

    def username
      @session.me.name
    end

    def inbox
      options = { :category=>'unread' }.freeze
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
        reply(text + footer, message)
      end
    end

    def analyze(message)
      username = message.author.name

      commands = [recent_command, subreddit_command, whisky_command]
      commands.each do |command|
        results = command.match(username, message.body) # TODO: handle submissions
        results.map {|result| build_reply(result, message.author.name)}
      end.flatten.join("\n")
    end

    def build_reply(result, username)
      return '' if result.return_value.nil?
      reply_body = "/u/#{username}'s latest reviews"
      reply_body += " (#{result.parameters.first})" if !result.parameters.empty?
      reply_body += "\n\n"
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
      message.reply(text)
    end

    private

    def footer
      "___\n^("\
        "More info? Ask /u/FlockOnFire or read "\
        "[here](https://github.com/FlockBots/ReviewBot)"\
        ")"
    end

    def recent_command
      prefix = "/u/#{username} latest"
      regex = /#{Regexp.quote(prefix)}/i
      ParameterizedCommand.new(regex) do |username|
        @repository.recent_reviews(username)
      end
    end

    def subreddit_command
      prefix = "/u/#{username} /r/"

      # command taken from reddit source: reddit/reddit: r2/models/subreddit.py
      subreddit = /[A-Za-z0-9][A-Za-z0-9_]{2,20}/
      regex = /#{Regexp.quote(prefix)}(#{subreddit})($|[^A-Za-z0-9_])/i
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
