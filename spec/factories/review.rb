FactoryBot.define do
  sequence(:whisky) do |n|
    @whiskies = ['Caol Ila', 'Talisker', 'Glenmorangie', 'Heartwood', 'Ardbeg',
                 'Port Charlotte', 'Glenfarclas', 'Ardbeg Uigeadail',
                 'Glenmorangie Quinta Ruban', 'Springbank', 'Blairmhor']
    @whiskies[n % @whiskies.count]
  end

  sequence(:region) do |n|
    @regions = ['Islay', 'Islay', 'Speyside', 'Australia', 'Islay', 'Islay',
                'Speyside', 'Islay', 'Highlands', 'Speyside', 'Speyside']
    @regions[n % @regions.count]
  end

  sequence(:redditor) do |n|
    @users = ['FlockOnFire', 'throwboats', 'razzafrachen', 'unclimbability']
    @users[n % @users.count]
  end

  sequence(:subreddit) do |n|
    @subs = ['Scotch', 'Bourbon', 'WorldWhisky']
    @subs[n % @subs.count]
  end

  sequence(:rating) do |n|
    n % 101
  end

  sequence (:url) do |n|
    "http://reddit.com/r/scotch/#{n}"
  end

  factory :review do
    whisky
    region
    redditor
    subreddit
    rating
    url
    published_at Time.now
  end
end