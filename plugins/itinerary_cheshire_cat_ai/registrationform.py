from cat.experimental.form import form, CatForm, CatFormState 
from cat.log import log
from .meilisearch import save
from .itinerary import Itinerary 
from pydantic import ValidationError

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
        prompt = ""
        if save(form_model):
            prompt = "Il tuo compito è quello di dire all'utente che l'itinerario è stato registrato con successo."
        else :
            prompt = "Il tuo compito è quello di dire all'utente che sfortunatamente non è stato possibile registrare l'itinerario e di riprovare in seguito."
        out = self.cat.llm(prompt)
        return {'output':out}
    
    def message(self):
        prompt = ""
        if self._state == CatFormState.CLOSED:
            prompt = "Il tuo compito è ringraziare l'utente per averti usato."
        if self._state == CatFormState.INCOMPLETE:
            missing_fields = ""
            if len(self._missing_fields) != 0:
                for field in self._missing_fields:
                    missing_fields += (field+" ")
                prompt = f"""Il tuo compito è dire all'utente di specificare i seguenti campi : {missing_fields} tradotti in italiano.
                Va inoltre riportato se un campo è opzionale, per fare ciò considera solo dove required è false nella seguente lista: 
                {[field for name,field in self.model_class.__fields__.items()]}
                """
            if len(self._errors) != 0:
                prompt += f"""Elencare all'utente i seguenti errori: {self._errors}"""
        if self._state == CatFormState.WAIT_CONFIRM:
            prompt= f"""Il tuo compito è quello di riepilogare i 
            campi presenti nel seguente dizionario {self._model} come se fossero i campi
            di registrazione 
            e chiedere all'utente se vuole confermare la registrazione dell'itinerario"""
        out = self.cat.llm(prompt)
        return {'output' : out}
    
    def validate(self, model):
        self._missing_fields = []
        self._errors = []
        try:
            model = self.model_class(**model).model_dump(mode="json")
            self._state = CatFormState.COMPLETE
        except ValidationError as e:
            for error_message in e.errors():
                loc = error_message.get("loc", [])
                if loc and len(loc) > 0: #QUESTA COSA NON MI PIACE :(
                    field_name = loc[0]
                    if error_message["type"] == "missing":
                        self._missing_fields.append(field_name)
                    else:
                        self._errors.append(f'{field_name}: {error_message["msg"]}')
                    
                        if field_name in model:
                         del model[field_name]
                else:
                    self._errors.append(f'{error_message["msg"]}')
            self._state = CatFormState.INCOMPLETE

        return model
    
