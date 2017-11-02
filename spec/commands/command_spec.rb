include ReviewBot::Commands

describe Command do
  let(:match_result) { 97 }
  subject do
    described_class.new(/rspec/) { match_result }
  end
  describe '#match' do
    it 'calls the block if the regex matches the phrase' do
      calls = subject.match('rspec is fantastic!')
      expect(calls.first.return_value).to eq match_result
    end

    it 'returns nil if the regex does not match the phrase' do
      calls = subject.match('ruby is fantastic!')
      expect(calls).to be_empty
    end
  end
end
