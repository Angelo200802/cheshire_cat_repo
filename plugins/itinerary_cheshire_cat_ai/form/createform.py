from cat.experimental.form import form, CatForm, CatFormState
from ..utility import get_automa
from ..finit_state_machine.automa import Automa

@form
class CreateItineraryForm(CatForm):
    description = ""
    start_examples = ["Dammi qualche suggerimento per un itinerario","Hai qualche proposta per un viaggio?",
                    "Mi daresti qualche idea per un percorso da seguire?","Quali luoghi mi consiglieresti di visitare?",
                    "suggeriscimi un itinerario","Puoi consigliarmi un itinerario?",
                    "Vorrei sapere se hai suggerimenti per un itinerario interessante","Puoi suggerirmi un percorso da esplorare?",
                    "Hai qualche raccomandazione per un itinerario?","Mi servirebbero consigli su dove andare durante il viaggio",
                    "Quali attrazioni dovrei includere nel mio itinerario?",
                    "Vorrei creare un itinerario","Mi piacerebbe pianificare un itinerario.","Ho intenzione di organizzare un percorso di viaggio.",
                    "Voglio mettere insieme un itinerario.","Desidero strutturare un itinerario.","Sto pensando di creare un percorso di viaggio.",
                    "Vorrei progettare un itinerario.","Mi interessa elaborare un itinerario.","Voglio definire un percorso per il mio viaggio.",
                    "Ho bisogno di preparare un itinerario.","Sto cercando di costruire un percorso di viaggio.",
                    "Organizza un itinerario utilizzando queste tappe.","Pianifica un percorso considerando le seguenti destinazioni."
                    "Metti insieme un itinerario partendo da queste tappe.","Sviluppa un itinerario basato sui luoghi indicati."
                    ,"Costruisci un percorso utilizzando le seguenti tappe.","Elabora un itinerario tenendo conto di queste destinazioni.",
                    "Progetta un percorso seguendo le tappe elencate.","Imposta un itinerario considerando le seguenti località.",
                    "Definisci un percorso basato su queste tappe.","Crea un tragitto seguendo le destinazioni indicate."]
    stop_examples = ["stop"]

    state_machine : Automa 

    def __init__(self,cat):
        super().__init__(cat)
        self.state_machine = get_automa(cat)
        
    
    def next(self):
        out = self.state_machine.execute_transition()
        if self.state_machine.get_cur_state() == self.state_machine.get_final_state():
            self._state = CatFormState.CLOSED
        return out
        

