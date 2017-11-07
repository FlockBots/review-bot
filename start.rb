require 'logger'

require 'dotenv'
require 'redd'

require_relative 'lib/reviewbot'

Dotenv.load '.env' if File.exists? '.env'

db = File.expand_path(ENV['RB_DB'])
repository = ReviewBot::Repositories::Sqlite.new(10, db)

session = Redd.it(
  user_agent: ENV['RB_USER_AGENT'],
  client_id:  ENV['RB_CLIENT_ID'],
  secret:     ENV['RB_SECRET'],
  username:   ENV['RB_USERNAME'],
  password:   ENV['RB_PASSWORD']
)

logfile = ENV['DB_LOGFILE'] || STDOUT
logger = Logger.new(logfile, level: ENV['RB_LOGLEVEL'])

bot = ReviewBot::Bot.new(session, repository, logger)
bot.watch_reddit
