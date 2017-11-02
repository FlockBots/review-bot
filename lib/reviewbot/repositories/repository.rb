module ReviewBot
  module Repositories
    class Repository
      attr_accessor :user

      def initialize(limit)
        @limit = limit
      end

      def recent_reviews(limit)
        raise NotImplementedError
      end

      def subreddit_reviews(limit, subreddit)
        raise NotImplementedError
      end

      def whisky_reviews(limit, whisky)
        raise NotImplementedError
      end
    end
  end
end
