include ReviewBot::Commands

describe ParameterizedCommand do
  def yoda(noun, adjective)
    "#{adjective.capitalize}, #{noun} is."
  end

  subject do
    described_class.new(/([a-z]+) is ([a-z]+)/, [0, 1], &method(:yoda))
  end
  describe '#match' do
    let(:noun) { 'rspec' }
    let(:adjective) { 'fantastic' }

    it 'calls the block with the captured arguments if the regex matches' do
      call = subject.match("#{noun} is #{adjective}")
      expect(call.count).to eq 1
      results = call.first.result
      parameters = call.first.parameters
      expect(results).to eq yoda(noun, adjective)
      expect(parameters).to eq [noun, adjective]
    end

    it 'can handle multiple matches' do
      call = subject.match("#{noun} is #{adjective} and ruby is cool")
      expect(call.count).to eq 2
      results = call.map(&:result)
      parameters = call.map(&:parameters)
      expect(results).to eq [yoda(noun, adjective), yoda('ruby', 'cool')]
      expect(parameters).to eq [[noun, adjective], ['ruby', 'cool']]
    end

    it 'returns nil if the regex does not match the phrase' do
      result = subject.match('1 + 1 is two')
      expect(result).to be_empty
    end
  end
end
