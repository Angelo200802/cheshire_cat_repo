import random
from pydantic import BaseModel
from cat.experimental.form import form, CatForm, CatFormState 
from cat.log import log

class GiocoNumero(BaseModel):
    your_number : int

@form
class GiocoNumeroForm(CatForm):
    description = "Form per giocare ad indovina un numero"
    model_class = GiocoNumero
    ask_confirm = False
    start_examples = ['Giochiamo ad indovina un numero']
    stop_examples = ['Stop gioco']
    rounds : int = 3
    cur_round : int = 0
    cpu_score : int = 0
    your_score : int = 0

    def submit(self,form_data):
        out = ""
        if self.cpu_score > self.your_score:
            prompt = "Il tuo compito è quello di dire all'utente che ha perso"
            out = self.cat.llm(prompt)
        elif self.cpu_score < self.your_score:
            prompt = "Il tuo compito è quello di dire all'utente che ha vinto"
            out = self.cat.llm(prompt)
        return {'output' : out}
    

    def next(self):
        out = ""
        if self._state == CatFormState.INCOMPLETE :
            prompt = "Il tuo compito è quello di dire all'utente di scrivere un numero."
            out = self.cat.llm(prompt)
            self._state = CatFormState.COMPLETE
        else :
            self.update()
            num = int(self._model["your_number"])
            if self.cur_round < self.rounds :
                x = random.randint(0,11)
                if x == num:
                    cat.send_ws_message(f"Bravo hai indovinato")
                    self.your_score += 1
                else : 
                    cat.send_ws_message(f"Sbagliato stavo pensando a {x}")
                    self.cpu_score += 1
                if abs(self.your_score - self.cpu_score):
                    self._state = CatFormState.CLOSED
                else:
                    self._state = CatFormState.INCOMPLETE
                    self.cur_iteration += 1               
            else:
                self._state = CatFormState.CLOSED
                self.submit({})
        return {'output':out}
        
