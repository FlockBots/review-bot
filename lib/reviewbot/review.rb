module ReviewBot
  Review = Struct.new(:whisky, :region, :redditor, :url, :subreddit, :rating,
             :published_at)
end