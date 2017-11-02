module ReviewBot
  module Commands
  end
end

%w(command_result command parameterized_command)
  .each { |file| require_relative File.join('commands', file) }
