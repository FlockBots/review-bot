require 'better-logger'
require 'dotenv'
require 'redd'

def load_environment
  Dotenv.load '.env' if File.exists? '.env'
end

def create_session
  session = Redd.it(
    user_agent: ENV.fetch('RB_USER_AGENT'),
    client_id:  ENV.fetch('RB_CLIENT_ID'),
    secret:     ENV.fetch('RB_SECRET'),
    username:   ENV.fetch('RB_USERNAME'),
    password:   ENV.fetch('RB_PASSWORD'),
    max_retries: ENV.fetch('RB_RETRIES', 0)
  )
end

def create_logger
  level = ENV['RB_LOGLEVEL'] || 'info'
  Better::Logger.config :logger do |conf|
    conf.color     = false
    conf.log_to    = ENV.fetch('RB_INFOLOG', STDOUT)
    conf.error_to  = ENV.fetch('RB_ERRORLOG', STDERR)
    conf.log_level = level.to_sym
  end
  logger
end
