include ReviewBot::Commands

describe ParameterizedCommand do

  def yoda(noun, adjective)
    "#{adjective.capitalize}, #{noun} is."
  end

  subject do
    described_class.new(/^(\w+) is (\w+)$/, [0, 1], &method(:yoda))
  end
  describe '#match' do
    let(:noun) { 'rspec' }
    let(:adjective) { 'fantastic' }

    it 'calls the block with the captured arguments if the regex matches' do
      result = subject.match("#{noun} is #{adjective}")
      expect(result).to eq yoda(noun, adjective)
    end

    it 'returns nil if the regex does not match the phrase' do
      result = subject.match("#{noun} is also #{adjective}")
      expect(result).to be nil
    end
  end
end
