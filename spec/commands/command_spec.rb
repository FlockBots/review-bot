include ReviewBot::Commands

describe Command do
  let(:match_result) { 97 }
  subject do
    described_class.new(/rspec/) { match_result }
  end
  describe '#match' do
    it 'calls the block if the regex matches the phrase' do
      call = subject.match('rspec is fantastic!')
      expect(call.first.result).to eq match_result
    end

    it 'returns nil if the regex does not match the phrase' do
      call = subject.match('ruby is fantastic!')
      expect(call).to be_empty
    end
  end
end
