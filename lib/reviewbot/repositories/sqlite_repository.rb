require 'sqlite3'

module ReviewBot
  module Repositories
    class Sqlite < Repository
      def initialize(limit, database)
        @db = SQLite3::Database.new database
        super(limit)
      end

      def recent_reviews(username)
        raise NotImplementedError
      end

      def subreddit_reviews(username, subreddit)
        raise NotImplementedError
      end

      def whisky_reviews(username, whisky)
        raise NotImplementedError
      end
    end
  end
end
