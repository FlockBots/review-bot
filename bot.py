import re

class Bot:
    def __init__(self):
        self.callbacks = {}
        pass

    def register(self, regex):
        """ Decorator to register callbacks """
        def wrapper(function):
            print('Registered function on ' + regex)
            try:
                self.callbacks[regex].append(function)
            except KeyError:
                self.callbacks[regex] = [function]
            return function
        return wrapper

    def check_callbacks(self, string):
        for regex, functions in self.callbacks.items():
            match = re.match(regex, string)
            if match:
                for callback in functions:
                    callback(match)

bot = Bot()

@bot.register('.*')
def meep(match):
    print(match)

@bot.register('Flock(.*)')
def username(match):
    print(match.group(1))

bot.check_callbacks("Flock's on Fire!")