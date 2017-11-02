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
      result = subject.match("#{noun} is #{adjective}")
      expect(result).to eq [yoda(noun, adjective)]
    end

    it 'can handle multiple matches' do
      result = subject.match("#{noun} is #{adjective} and ruby is cool")
      expect(result). to eq [yoda(noun, adjective), yoda('ruby', 'cool')]
    end

    it 'returns nil if the regex does not match the phrase' do
      result = subject.match("1 + 1 is two")
      expect(result).to be nil
    end
  end
end
