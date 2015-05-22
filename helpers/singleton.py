class Singleton(type):
    _instance = None

    def __call__(_class, *args, **kwargs):
        if not _class._instance:
            _class._instance = super(Singleton, _class).__call__(*args, **kwargs)
        return _class._instance
