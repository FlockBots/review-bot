include ReviewBot
include ReviewBot::Commands

describe Bot do
  let(:username) { 'review_bot' }
  let(:user) { double(:user, name: username )}
  let(:session) { double(:session, me: user) }
  let(:repository) { double(:repository) }

  let(:valid_subreddits) do
    # start with letter or number, 3-21 characters
    %w(scotch
       bourbon
       worldwhiskey
       all
       123456789012345678901
    )
  end
  let(:invalid_subreddits) do
    %w(2s
       _leading_underscore
       a_larger_than_21_chars
    )
  end

  subject do
    Bot.new(session, repository)
  end

  describe '#recent_command' do
    it 'matches on name followed by "latest"' do
      expect(repository).to receive(:recent_reviews).and_return([])
      result = subject.send(:recent_command).match("/u/#{username} latest")
      expect(result).to_not be_empty
    end

    it 'does not match on just the username ' do
      expect(repository).to_not receive(:recent_reviews)
      result = subject.send(:recent_command).match("/u/#{username}")
      expect(result).to be_empty
    end

    it 'does not match on just the username followed by other text' do
      expect(repository).to_not receive(:recent_reviews)
      result = subject.send(:recent_command).match("/u/#{username} lorem ipsum")
      expect(result).to be_empty
    end
  end

  describe '#subreddit_command' do
    it 'matches on name followed by "/r/" and a valid subreddit name' do
      subreddit = valid_subreddits.sample
      expect(repository).to receive(:subreddit_reviews)
                        .with(subreddit)
                        .and_return([])
      result = subject.send(:subreddit_command)
                      .match("/u/#{username} /r/#{subreddit}")
      expect(result).to_not be_nil
    end

    it 'does not match on invalid subreddit names' do
      subreddit = invalid_subreddits.sample
      expect(repository).to_not receive(:subreddit_reviews)
      result = subject.send(:subreddit_command)
                      .match("/u/#{username} /r/#{subreddit}")
      expect(result).to be_empty
    end
  end

  describe '#whisky_command' do
    it 'matches on name followed by a string surrounded by single quotes' do
      expect(repository).to receive(:whisky_reviews)
                        .with("Sir William's Scotch")
                        .and_return([])
      result = subject.send(:whisky_command)
                      .match("/u/#{username} 'Sir William\\'s Scotch'")
      expect(result).to_not be_empty
      parameter = result.first.parameters.first
      expect(parameter).to eq "Sir William's Scotch"
    end

    it 'matches on name followed by a string surrounded by double quotes' do
      expect(repository).to receive(:whisky_reviews)
                        .with("Sir William's Scotch")
                        .and_return([])
      result = subject.send(:whisky_command)
                      .match("/u/#{username} \"Sir William's Scotch\"")
      expect(result).to_not be_empty
      parameter = result.first.parameters.first
      expect(parameter).to eq "Sir William's Scotch"
    end

    it 'does not match on mismatching quotes' do
      expect(repository).to_not receive(:whisky_reviews)
      result = subject.send(:whisky_command)
                      .match("/u/#{username} \"Caol Ila'")
      expect(result).to be_empty
    end
  end
end
