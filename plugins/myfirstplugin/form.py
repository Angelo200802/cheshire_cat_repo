from pydantic import BaseModel
from cat.experimental.form import form, CatForm, CatFormState 
from cat.log import log

class Anagrafe(BaseModel):
    nome : str
    cognome: str

@form
class AnagrafeForm(CatForm):
    description = "Form per la registrazione di un utente"
    model_class = Anagrafe
    ask_confirm = True
    start_examples = ['Vorrei registrarmi']
    stop_examples = ['Stop registrazione']

    def submit(self,form_data):
        prompt = f"""Il tuo compito è quello di dire all'utente che è stato registrato"""
        out = self.cat.llm(prompt)
        return {'output':out+"\n Il form è chiuso."}
    
    def message(self):
        #log.info(f"Parametri: {dir(self._model['nome'])}")
        missing_fields = ""
        out = {}
        if self._missing_fields :
            for field in self._missing_fields:
                missing_fields += (field+" ")
            prompt = f"Il tuo compito è quello di dire all'utente che mancano i seguenti campi: {missing_fields}"
            out = self.cat.llm(prompt)
        elif self._state == CatFormState.WAIT_CONFIRM:
            log.info("Modello : "+str(self._model))
            prompt = "Il tuo compito è quello di chiedere all'utente di confermare la registrazione."
            out = self.cat.llm(prompt)
        return {'output':out}

        

