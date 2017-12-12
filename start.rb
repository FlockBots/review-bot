require 'better-logger'

require 'dotenv'
require 'redd'

require_relative 'lib/reviewbot'

File.write('reviewbot.pid', Process.pid)
Dotenv.load '.env' if File.exists? '.env'

db = File.expand_path(ENV['RB_DB'])
repository = ReviewBot::Repositories::Sqlite.new(10, db)

session = Redd.it(
  user_agent: ENV['RB_USER_AGENT'],
  client_id:  ENV['RB_CLIENT_ID'],
  secret:     ENV['RB_SECRET'],
  username:   ENV['RB_USERNAME'],
  password:   ENV['RB_PASSWORD'],
  max_retries: ENV['RB_RETRIES'] || 0
)

infolog = ENV['RB_INFOLOG'] || STDOUT
errorlog = ENV['RB_ERRORLOG'] || STDERR
level = ENV['RB_LOGLEVEL'] || 'info'

Better::Logger.config :logger do |conf|
  conf.color     = false
  conf.log_to    = infolog
  conf.error_to  = errorlog
  conf.log_level = level.to_sym
end

logger.info('Starting new session.')

bot = ReviewBot::Bot.new(session, repository, logger)

retry_cap = 10 # 2**retry_cap seconds

begin
  bot.watch_reddit
  retries = 0
rescue HTTP::TimeoutError => e
  logger.error e
  raise e if retries > retry_cap
  retries += 1
  timeout = 2 ** retries
  logger.info "Retrying in #{timeout} seconds."
  sleep(timeout)
  retry
rescue => e
  logger.fatal e
  raise e
end
