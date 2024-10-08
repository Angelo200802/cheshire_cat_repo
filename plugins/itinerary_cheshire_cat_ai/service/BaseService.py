from abc import ABC, abstractmethod

class BaseService(ABC):

    @abstractmethod
    def save(self,form_model) -> bool:
        """Salva file da qualche parte."""
        pass

    @abstractmethod
    def search(self,query,limit) -> any:
        """Cerca i file."""
        pass

    @abstractmethod
    def get_filter_by_dict(self,model:dict):
        """Restituisce la query in base al dizionario"""
        pass

