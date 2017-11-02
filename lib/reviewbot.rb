module ReviewBot
end

reviewbot_path = File.expand_path('../reviewbot', __FILE__)

files = %w(commands
    repositories
    bot
).each { |file| require File.join(reviewbot_path, file) }
