from cat.experimental.form import form, CatForm
from ..finit_state_machine.chatbot_proxy import ChatbotProxy

@form
class CreateItineraryForm(CatForm):
    description = ""
    start_examples = ['Voglio creare un itinerario','Aggiungi al mio itinerario le seguenti tappe','Dammi un suggerimento per un itinerario']
    stop_examples = []

    proxy : ChatbotProxy 

    def __init__(self,cat):
        super().__init__(cat)
        self.proxy = ChatbotProxy(cat)
    
    def submit(self):
        prompt = """Ringrazia l'utente e invitalo a chiederti ulteriori cose"""
        out = self.cat.llm(prompt)
        return {"output":out}
    
    def next(self):
        out = self.proxy.next()
        if self.proxy.get_cur_state() == self.proxy.get_final_state():
            return self.submit()
        return out
        

