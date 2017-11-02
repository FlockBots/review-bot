module ReviewBot
  module Commands
    class ParameterizedCommand < Command
      def initialize(regex, indices, &callback)
        @indices = indices
        super(regex, &callback)
      end

      def match(phrase)
        matches = phrase.scan(@regex)
        matches.map do |captures|
          parameters = captures.values_at(*@indices)
          result = @callback.call(*parameters)
          CommandResult.new(parameters, result)
        end
      end
    end
  end
end
