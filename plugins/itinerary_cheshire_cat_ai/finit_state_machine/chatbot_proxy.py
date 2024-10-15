from automat import TypeMachine
from ..utility import method_state, get_machine

class ChatbotProxy:

    def __init__(self,cat):
        self.machine = get_machine(cat)
        #self.method_state = method_state() #devo memorizzare tutti gli stati con i metodi associati
        self.method_state = {'init' : self.machine.ask_advice}
        self.cur_state = next(iter(self.method_state)) #Bisogna mettere il primo stato come primo elemento del dizionario

    def next(self) -> dict:
        if self.cur_state in self.method_state:
            return self.method_state[self.cur_state]()
        else:
            raise ValueError("Errore: lo stato corrente non esiste.")
    
    def set_cur_state(self,state):
        self.cur_state = state
        print(f"STATE = {self.cur_state}")

