from abc import ABC, abstractmethod

class Automa(ABC):

    @abstractmethod
    def get_cur_state(self):
        pass

    @abstractmethod
    def get_final_state(self):
        pass

    @abstractmethod
    def execute_transition(self):
        pass