from cat.experimental.form import form, CatForm, CatFormState 
from .registrationform import Itinerary
from .meilisearch import search
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
    limit = 3
    attempt = 0

    def submit(self,form_model):
        prompt = """Il tuo compito è ringraziare l'utente per averti usato"""
        out = self.cat.llm(prompt)
        return {'output':out}
    
    def create_query_filter(self) -> list:
        query_filter = []
        for field in self._model:
                query_filter.append(f'{field} = "{self._model[field]}"')
        return query_filter
        
    
    def message(self):
        prompt = ""
        if self._state == CatFormState.WAIT_CONFIRM:
            filter = self.create_query_filter()
            try:
                results = search(filter,self.limit)
                if len(results['hits']) == 0 :
                    self._state = CatFormState.INCOMPLETE
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
        if self._state == CatFormState.INCOMPLETE:
            if len(self._errors) != 0:
               log.info(self._errors)
               prompt = f"""Il tuo compito è quello di elencare all'utente i seguenti errori : {self._errors}"""
            else :
               prompt = f"""Il tuo compito è quello di dire all'utente che può specificare uno o più dei seguenti campi per 
               effettuare una ricerca : {self.model_class.model_fields}"""
        if self._state == CatFormState.CLOSED:
            return self.submit(self._model)
        out = self.cat.llm(prompt)
        return {'output' : out}
    
    
    def next(self):
        if self._state == CatFormState.WAIT_CONFIRM:
            if self.confirm():
                self._state = CatFormState.CLOSED
                return self.submit(self._model)
            else:
                #if self.check_exit_intent():
                    #self._state = CatFormState.CLOSED
                #else:
                    self._state = CatFormState.INCOMPLETE
                    self.attempt += 1
                    if self.attempt % 5 == 0:
                        self.limit += 1
                    self._model = {}

        if self.check_exit_intent():
            self._state = CatFormState.CLOSED

        if self._state == CatFormState.INCOMPLETE:
            self._model = self.update()
            filter = self.create_query_filter()
            if len(filter) != 0:
                self._state = CatFormState.WAIT_CONFIRM
        if self._state == CatFormState.COMPLETE:
            if self.ask_confirm:
                self._state = CatFormState.WAIT_CONFIRM
            else:
                self._state = CatFormState.CLOSED
                return self.submit(self._model)
        return self.message()
    
    def extraction_prompt(self):
        history = self.cat.working_memory.user_message_json
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