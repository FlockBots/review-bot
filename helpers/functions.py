import itertools


def peek(generator):
    """ Take a generator and look at the first object without removing it

        Args: 
            generator: the generator to inspect
        Result:
            None, None: if the generator is empty
            Otherwise a single object, the first one from the generator
    """
    try:
        first = next(generator)
    except StopIteration:
        # Generator is empty
        return None, None
    except TypeError:
        if len(generator) > 0:
            return generator[0], generator
        else:
            return None, None
    else:
        return first, itertools.chain([first], generator)
