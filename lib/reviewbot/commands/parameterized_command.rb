module ReviewBot
  module Commands
    class ParameterizedCommand < Command
      def initialize(regex, indices=[], &callback)
        @indices = indices
        super(regex, &callback)
      end

      def match(phrase, *args)
        matches = phrase.scan(@regex)
        matches.map do |captures|
          raise 'Expected regex to have capture groups' if !captures.is_a? Array
          arguments = args + captures.values_at(*@indices)
          result = @callback.call(*arguments)
          CommandResult.new(arguments, result)
        end
      end
    end
  end
end
