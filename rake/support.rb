require 'better-logger'
require 'dotenv'
require 'redd'

def load_environment
  Dotenv.load '.env' if File.exists? '.env'
end

def create_session
  session = Redd.it(
    user_agent: ENV['RB_USER_AGENT'],
    client_id:  ENV['RB_CLIENT_ID'],
    secret:     ENV['RB_SECRET'],
    username:   ENV['RB_USERNAME'],
    password:   ENV['RB_PASSWORD'],
    max_retries: ENV['RB_RETRIES'] || 0
  )
end

def create_logger
  level = ENV['RB_LOGLEVEL'] || 'info'
  Better::Logger.config :logger do |conf|
    conf.color     = false
    conf.log_to    = ENV['RB_INFOLOG'] || STDOUT
    conf.error_to  = ENV['RB_ERRORLOG'] || STDERR
    conf.log_level = level.to_sym
  end
  logger
end
