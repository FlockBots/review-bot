module ReviewBot
  module Commands
    class ParameterizedCommand < Command
      def initialize(regex, indices, &callback)
        @indices = indices
        super(regex, &callback)
      end

      def match(phrase)
        data = @regex.match phrase
        return nil if data.nil?
        parameters = @indices.map {|i| data.captures[i]}
        @callback.call(*parameters)
      end
    end
  end
end
