from pydantic import BaseModel, ValidationError,Field, field_validator, model_validator
from cat.experimental.form import form, CatForm, CatFormState 
from cat.log import log
from .rep import save, search
import re
from datetime import datetime
import copy 

class Itinerary(BaseModel):
    country : str = Field(description="Città in cui si vorrebbe andare")
    start_date : str = Field(description="Data inizio itinerario")
    finish_date : str = Field(description="Data di fine dell'itinerario")
    budget : float = Field(description="Budget di spesa per l'itinearario",g=0)
    description : str = Field(description="Descrizione delle attività dell'itinerario")

    @field_validator('country')
    def check_fields(cls,c):
        if not re.match(r'^[a-zA-Z\s]+$', c):
            raise ValueError("La città inserita non è valida")
        return c
    
    @field_validator('budget')
    def check_budget(cls,b):
        if b < 0:
            raise ValueError("Non puoi inserire un valore minore di 0")
        b = round(b,2)
        return b
    @field_validator('start_date')
    def check_start_date(cls,sd):
        if not re.match(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$',sd) :
            raise ValueError("La data di inizio non è valida")
        if datetime.strptime(sd,"%d/%m/%Y") < datetime.now():
            raise ValueError("L'itinerario non può partire da giorni precedenti a oggi")
        return sd
    
    @field_validator('finish_date')
    def check_finish_date(cls,fd):
        if not re.match(r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$',fd) :
            raise ValueError("La data di fine non è valida")
        return fd
    

    #@model_validator(mode="after")
    #def check_date(self):
    #    start = datetime.strptime(self.start_date,"%d/%m/%Y")
    #    finish = datetime.strptime(self.finish_date,"%d/%m/%Y")
    #    if start > finish:
    #        raise ValueError("Le date non sono valide")
    #    if start < datetime.now():
    #        raise ValueError("La data di inizio non è valida")
    #    return self
    
@form
class ItineraryRegistrationForm(CatForm):
    description = "Form di registrazione di un itinerario"
    ask_confirm = True
    start_examples = ['Vorrei creare il seguente itinerario',
                      'Voglio registrare un itinerario',
                      'Vorrei creare un itinerario']
    stop_examples = ['Stop alla registrazione',
                     "Ferma la registrazione"]
    model_class = Itinerary


    def submit(self,form_model):
        out = ""
        if save(form_model):
            prompt = "Il tuo compito è quello di dire all'utente che l'itinerario è stato registrato con successo."
            out = self.cat.llm(prompt)
        else :
            prompt = "Il tuo compito è quello di dire all'utente che sfortunatamente non è stato possibile registrare l'itinerario e di riprovare in seguito."
            out = self.cat.llm(prompt)
        return {'output':out}
    
    def message(self):
        prompt = ""
        if self._state == CatFormState.INCOMPLETE:
            missing_fields = ""
            if len(self._missing_fields) != 0:
                for field in self._missing_fields:
                    missing_fields += (field+" ")
                prompt = f"""Il tuo compito è dire all'utente di specificare i seguenti campi : {missing_fields} tradotti in italiano"""
            if len(self._errors) != 0:
                prompt += f"""Il tuo compito è dire all'utente che i seguenti campi sono invalidi {self._errors} nel seguente formato:
                field : messaggio"""
        if self._state == CatFormState.WAIT_CONFIRM:
            prompt= f"""Il tuo compito è quello di riepilogare i 
            campi presenti nel seguente dizionario {self._model} come se fossero i campi
            di registrazione 
            e chiedere all'utente se vuole confermare la registrazione dell'itinerario"""
        out = self.cat.llm(prompt)
        return {'output' : out}
    
        
@form 
class ItinerarySearchForm(CatForm):
    description = "Form di ricerca di un itinerario"
    ask_confirm = True
    start_examples = ['Vorrei trovare un itinerario',
                      'Vorrei andare a']
    stop_examples = ['Ferma la ricerca']
    model_class = Itinerary
    miss_fields = 5
    
    def submit(self,form_model):
        self.len_old_model = 0
        prompt = """Il tuo compito è ringraziare l'utente per averti usato"""
        out = self.cat.llm(prompt)
        return {'output':out}
    
    def create_query_filter(self) -> []:
        query_filter = []
        for field in self._model:
            query_filter.append(f'{field} = "{self._model[field]}"')
        log.info(query_filter)
        return query_filter
        
    
    def message(self):
        prompt = ""
        if self._state == CatFormState.WAIT_CONFIRM:
            filter = self.create_query_filter()
            results = search(filter)
            if len(results['hits']) == 0 :
                self._state = CatFormState.INCOMPLETE
            else:
                prompt = f"""Il tuo compito è quello di dire all'utente che i risultati della ricerca 
            sono quelli presenti nel seguente dizionario {results['hits']} in italiano,escludendo il campo id,
            chiedere se i risultati della ricerca vanno bene. Nota bene {results['hits']} non deve essere usato
            per completare json dalla conversazione. """
                
        if self._state == CatFormState.INCOMPLETE:
            if 'country' in self._missing_fields:
                prompt = "Il tuo compito è quello di chiedere all'utente in che città vorrebbe andare"
            elif 'start_date' in self._missing_fields:
                prompt = f"""Il tuo compito è quello di chiedere all'utente quando vorrebbe partire"""
            elif 'budget' in self._missing_fields:
                prompt = f"""Il tuo compito è quello di chiedere all'utente quanto vorrebbe spendere di budget"""
            elif 'finish_date' in self._missing_fields:
                prompt = f"""Il tuo compito è quello di chiedere all'utente quando vorrebbe tornare dal viaggio"""
            else:
                prompt = """Il tuo compito è quello di avvisare l'utente che la purtroppo non è stato possibile
                            trovare itinerari adatti"""
                self._state = CatFormState.CLOSED
        out = self.cat.llm(prompt)
        return {'output' : out}
    
    
    def next(self):

        if self._state == CatFormState.WAIT_CONFIRM:
            if self.confirm():
                self._state = CatFormState.CLOSED
                return self.submit(self._model)
            else:
                if self.check_exit_intent():
                    self._state = CatFormState.CLOSED
                else:
                    self._state = CatFormState.INCOMPLETE

        if self.check_exit_intent():
            self._state = CatFormState.CLOSED

        if self._state == CatFormState.INCOMPLETE:
            self._model = self.update()
            if self.miss_fields > len(self._missing_fields) and len(self._missing_fields) > 0:
                self._state = CatFormState.COMPLETE
                self.miss_fields = len(self._missing_fields)

        if self._state == CatFormState.COMPLETE:
            if self.ask_confirm:
                self._state = CatFormState.WAIT_CONFIRM
            else:
                self._state = CatFormState.CLOSED
                return self.submit(self._model)
        return self.message()

