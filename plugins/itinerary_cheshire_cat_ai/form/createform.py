from cat.experimental.form import form, CatForm
from ..utility import get_automa
from ..finit_state_machine.automa import Automa

@form
class CreateItineraryForm(CatForm):
    description = ""
    start_examples = ['Voglio creare un itinerario','Aggiungi al mio itinerario le seguenti tappe','Dammi un suggerimento per un itinerario']
    stop_examples = []

    state_machine : Automa 

    def __init__(self,cat):
        super().__init__(cat)
        self.state_machine = get_automa(cat)
        
    
    def submit(self,model):
        prompt = """Ringrazia l'utente e invitalo a chiederti ulteriori cose"""
        out = self.cat.llm(prompt)
        return {"output":out}
    
    def next(self):
        out = self.state_machine.execute_transition()
        if self.state_machine.get_cur_state() == self.state_machine.get_final_state():
            return self.submit({})
        return out
        

