module ReviewBot
  module Commands
    class Command
      def initialize(regex, &callback)
        @regex = regex
        @callback = callback
      end

      def match(phrase)
        result = @callback.call if @regex.match? phrase
        CommandResult.new([], result)
      end
    end
  end
end
