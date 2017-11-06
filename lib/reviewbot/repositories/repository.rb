module ReviewBot
  module Repositories
    class Repository
      def initialize(limit)
        @limit = limit
      end

      def recent_reviews
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
