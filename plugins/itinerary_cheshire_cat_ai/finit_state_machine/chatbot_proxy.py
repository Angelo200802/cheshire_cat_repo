from automat import TypeMachine
from ..utility import method_state, get_machine

class ChatbotProxy:

    def __init__(self,cat):
        self.machine : TypeMachine = get_machine(cat)
        #self.method_state = method_state() #devo memorizzare tutti gli stati con i metodi associati
        self.method_state = {'init' : self.machine.init ,
                            'ask_adv' : self.machine.ask_advice ,
                            'tell_adv' : self.machine.tell_advice ,
                            'ask_step' : self.machine.ask_step ,
                            'wait_conf_adv': self.machine.wait_confirm_advice ,
                            'confirm' : self.machine.confirm_result ,
                            'closed' : self.machine.closed }
        self.cur_state = next(iter(self.method_state)) #Bisogna mettere il primo stato come primo elemento del dizionario
        last_state = next(reversed(self.method_state))
        self.final_state = self.method_state[last_state]
    
    def next(self) -> dict:
        print(f"CURRENT STATE = {self.cur_state}, function = {self.method_state[self.cur_state]}")
        if self.cur_state in self.method_state:
            out = self.method_state[self.cur_state]()
            if "callback" in out:
                out = out["callback"]()
            if 'next_state' in out: #bisogna aggiungere next_state per impostare il prossimo stato
                self.cur_state = out['next_state']
                out.pop('next_state',None) #per richiamare il prossimo metodo devo conoscere lo stato
            return out
        else:
            raise ValueError("Errore: lo stato corrente non esiste.")
    
    def get_cur_state(self):
        return self.cur_state
    
    def get_final_state(self):
        return self.final_state