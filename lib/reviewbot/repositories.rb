module ReviewBot::Repositories
end

files = %w(repository
    api_repository
    sqlite_repository
).each { |file| require_relative File.join('repositories', file) }
