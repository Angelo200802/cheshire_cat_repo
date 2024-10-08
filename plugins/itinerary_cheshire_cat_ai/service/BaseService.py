from abc import ABC, abstractmethod

class BaseService(ABC):

    @abstractmethod
    def save(self,form_model):
        """Salva file da qualche parte."""
        pass

    @abstractmethod
    def search(self,query,limit):
        """Cerca i file."""
        pass

