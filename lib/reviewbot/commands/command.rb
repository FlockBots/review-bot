module ReviewBot
  module Commands
    class Command
      def initialize(regex, &callback)
        @regex = regex
        @callback = callback
      end

      def match(phrase)
        matches = phrase.scan(@regex)
        matches.map do
          result = @callback.call
          CommandResult.new([], result)
        end
      end
    end
  end
end
