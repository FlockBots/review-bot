require 'sqlite3'

module ReviewBot
  module Repositories
    class Sqlite < Repository
      def initialize(limit, database)
        @db = SQLite3::Database.new database
        super(limit)
      end

      def columns
        %w(whisky
            region
            redditor
            url
            subreddit
            rating
            published_at).join(', ')
      end

      def limit
        "LIMIT #{@limit}"
      end

      def order
        "ORDER BY published_at DESC"
      end

      def recent_reviews
        query = <<-SQL.strip
          SELECT #{columns} FROM database_reviews WHERE redditor = ? #{order} #{limit}
        SQL
        p query
        results = @db.execute(query, [user])
        results.map { |result| ReviewBot::Review.new(*result) }
      end

      def subreddit_reviews(username, subreddit)
        raise NotImplementedError
      end

      def whisky_reviews(username, whisky)
        raise NotImplementedError
      end

      private



    end
  end
end
