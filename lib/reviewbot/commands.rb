module ReviewBot
  module Commands
  end
end

files = %w(command
    parameterized_command
).each { |file| require_relative File.join('commands', file) }
