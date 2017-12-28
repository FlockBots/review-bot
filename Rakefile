require 'rake/rspec'

require_relative './rake/support.rb'
require_relative './lib/reviewbot'

task default: :spec

task :run do
  load_environment
  session = create_session
  logger = create_logger

  db = File.expand_path(ENV['RB_DB'])
  repository = ReviewBot::Repositories::Sqlite.new(10, db)

  logger.info('Starting a new session.')
  bot = ReviewBot::Bot.new(session, repository, logger)

  retry_cap = 10

  begin
    retries = 0
    bot.watch_reddit
  rescue => e
    logger.error e
    raise e if retries > retry_cap
    retries += 1
    timeout = 2 ** retries
    logger.info("Retrying in #{timeout} seconds.")
    sleep(timeout)
    retry
  end
end
