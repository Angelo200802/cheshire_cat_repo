from cat.experimental.form import form, CatForm, CatFormState 
from ..model.itinerarymodel import Itinerary
from ..service.meili import MeiliService
from ..service.BaseService import BaseService
from pydantic import ValidationError
from cat.log import log
import json 

@form 
class ItinerarySearchForm(CatForm):
    description = "Form di ricerca di un itinerario"
    ask_confirm = True
    start_examples = ['Vorrei trovare un itinerario',
                      'Vorrei andare a',
                      'Vorrei cercare un itinerario']
    stop_examples = ['Ferma la ricerca',
                     'Stop ricerca']
    model_class = Itinerary
    service : BaseService = MeiliService('itinerary',Itinerary)
    limit = 3

    def submit(self,form_model):
        prompt = """Il tuo compito è ringraziare l'utente per averti usato"""
        out = self.cat.llm(prompt)
        return {'output':out}
        
    def message(self):
        prompt = ""
        if len(self._errors) != 0:
               log.error(self._errors)
               prompt = f"""Il tuo compito è quello di elencare all'utente i seguenti errori : {self._errors}"""
        elif self._state == CatFormState.WAIT_CONFIRM:
            filter = self.service.get_filter_by_dict(self._model)
            try:
                results = self.service.search(filter,self.limit)
                if len(results['hits']) == 0 :
                    prompt = f"""Il tuo compito è dire all'utente che non è stato trovato alcun risultato in base ai 
                    parametri da lui impostati."""
                else:
                    prompt = f"""
                    Il tuo compito è quello di dire all'utente che i risultati della ricerca 
                    sono quelli presenti nel seguente dizionario {results['hits']} escludendo il campo id e traducendo
                    il nome dei campi in italiano.
                    Infine chiedere se i risultati della ricerca vanno bene.
                    """
            except Exception as e:
                log.error(e)
                prompt = "Il tuo compito è quello di informare l'utente che la ricerca è fallita."    
        elif self._state == CatFormState.INCOMPLETE:
            if len(self._missing_fields) > 0:
                fields = self._missing_fields[0]
                log.info(self.model_class.model_fields)
                prompt = f"""Il tuo compito è quello di chiedere all'utente {self.model_class.model_fields[fields].description}."""
            else:
                self._state = CatFormState.CLOSED
        if self._state == CatFormState.CLOSED:
            return self.submit(self._model)
        out = self.cat.llm(prompt)
        return {'output' : out}
    
    
    def next(self):
        previous_state = self._state
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
            filter = self.service.get_filter_by_dict(self._model)
            if len(filter) != 0 and previous_state != CatFormState.WAIT_CONFIRM:
                self._state = CatFormState.WAIT_CONFIRM
        if self._state == CatFormState.COMPLETE:
            if self.ask_confirm:
                self._state = CatFormState.WAIT_CONFIRM
            else:
                self._state = CatFormState.CLOSED
                return self.submit(self._model)
        return self.message()
    
    def extraction_prompt(self):
        history = self.cat.working_memory.history
        history = [mex['message'] for mex in history if (mex['who'] == 'Human') or ('risultati' not in mex['message'] and mex['who'] == 'AI')]
        JSON_structure = "{"
        for field_name, field in self.model_class.model_fields.items():
            if field.description:
                description = field.description
            else:
                description = ""
            JSON_structure += f'\n\t"{field_name}": // {description} Must be of type `{field.annotation.__name__}` or `null`'  
        JSON_structure += "\n}"
        prompt = f"""Your task is to fill up a JSON out of a conversation.
The JSON must have this format:
```json
{JSON_structure}
```

This is the current JSON:
```json
{json.dumps(self._model, indent=4)}
```

This is the conversation:
{history}
All dates must be formatted as follows: dd/mm/yy
Updated JSON:
"""
        prompt_escaped = prompt.replace("{", "{{").replace("}", "}}")
        return prompt_escaped
    
    def validate(self, model):
        self._missing_fields = []
        self._errors = []
        try:
            model = self.model_class(**model).model_dump(mode="json")
            self._state = CatFormState.COMPLETE
        except ValidationError as e:
            for error_message in e.errors():
                loc = error_message.get("loc", [])
                if loc and len(loc) > 0:
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