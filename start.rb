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

logfile = File.open(ENV['RB_LOGFILE'], File::WRONLY | File::APPEND | File::CREAT)
logger = Logger.new(logfile, 3, 2 ** 20, level: ENV['RB_LOGLEVEL'])

bot = ReviewBot::Bot.new(session, repository, logger)
bot.watch_reddit
