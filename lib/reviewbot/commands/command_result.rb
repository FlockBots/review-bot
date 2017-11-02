module ReviewBot
  module Commands
    CommandResult = Struct.new(:parameters, :result) do
      def nil?
        result.nil?
      end
    end
  end
end