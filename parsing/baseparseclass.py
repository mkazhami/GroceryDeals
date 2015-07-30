from abc import ABCMeta, abstractmethod

class BaseParseClass:
    """
    The base parsing class for all stores
    """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def parse(self):
        pass
    
    