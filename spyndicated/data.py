from abc import ABCMeta, abstractmethod


class BaseHandler(metaclass=ABCMeta):

    def __init__(self, loc, *args, **kwargs):
        self.loc = loc
        self.conn_params = dict(**kwargs)

    @abstractmethod
    def insert(self, record):
        raise NotImplementedError

    @abstractmethod
    def insert_multi(self, records, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def select(self, identifiers):
        raise NotImplementedError
