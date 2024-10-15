from cat.experimental.form import form, CatForm
from ..finit_state_machine.chatbot_proxy import ChatbotProxy

@form
class CreateItineraryForm(CatForm):
    description = ""
    start_examples = ['Voglio creare un itinerario']
    stop_examples = []

    proxy : ChatbotProxy 

    def __init__(self,cat):
        super().__init__(cat)
        self.proxy = ChatbotProxy(cat)
    
    def next(self):
        out = self.proxy.next()
        if 'next_state' in out: #bisogna aggiungere next_state per impostare il prossimo stato
            self.proxy.set_cur_state(out['next_state']) 
            out.pop('next_state',None) #per richiamare il prossimo metodo devo conoscere lo stato
        return out

