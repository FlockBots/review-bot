include ReviewBot::Commands

describe Command do

  let(:match_result) { 97 }
  subject do
    described_class.new(/rspec/) { match_result }
  end
  describe '#match' do
    it 'calls the block if the regex matches the phrase' do
      result = subject.match('rspec is fantastic!')
      expect(result).to eq match_result
    end

    it 'returns nil if the regex does not match the phrase' do
      result = subject.match('ruby is fantastic!')
      expect(result).to be nil
    end
  end
end
