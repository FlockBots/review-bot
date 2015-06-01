import itertools


def peek(generator):
    ''' Take a generator and look at the first object without removing it

        Args: 
            generator: the generator to inspect
        Result:
            None: if the generator is empty
            Otherwise a single object, the first one from the generator
    '''
    try:
        first = next(generator)
    except StopIteration:
        # Generator is empty
        return None
    return first, itertools.chain([first], generator)
