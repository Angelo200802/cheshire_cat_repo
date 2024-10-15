from automat import TypeMachine
from ..utility import method_state, get_machine

class ChatbotProxy:

    def __init__(self,cat):
        self.machine : TypeMachine = get_machine(cat)
        #self.method_state = method_state() #devo memorizzare tutti gli stati con i metodi associati
        self.method_state = {'init' : self.machine.init}
        self.cur_state = next(iter(self.method_state)) #Bisogna mettere il primo stato come primo elemento del dizionario

    def next(self) -> dict:
        if self.cur_state in self.method_state:
            out = self.method_state[self.cur_state]()
            if 'next_state' in out: #bisogna aggiungere next_state per impostare il prossimo stato
                self.cur_state = out['next_state']
                out.pop('next_state',None) #per richiamare il prossimo metodo devo conoscere lo stato
            return out
        else:
            raise ValueError("Errore: lo stato corrente non esiste.")
    
    def get_cur_state(self):
        return self.cur_state

