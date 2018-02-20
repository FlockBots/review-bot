module ReviewBot
  Review = Struct.new(:whisky, :region, :redditor, :url, :subreddit, :rating,
             :published_at) do
                def rating_string(default = '--')
                  rating.nil? ? default : rating
                end
             end
end