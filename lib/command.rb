class Command
  def initialize(regex, callback)
    @regex = regex
    @callback = callback
  end

  def match(phrase)
    if @regex.match phrase
      @callback.call
    end
  end
end
