from cat.experimental.form import form, CatForm, CatFormState 
from ..service.service import Service
from pydantic import ValidationError, BaseModel
from cat.log import log
import json 
from ..utility import load_model
#from ..model.itinerarymodel import Itinerary

@form
class ItinerarySearchForm(CatForm):
    description = "Form di ricerca di un itinerario"
    ask_confirm = True
    start_examples = ['Vorrei trovare un itinerario',
                      'Vorrei andare a',
                      'Vorrei cercare un itinerario',
                      "Cerca un percorso per me",
                      "Mostrami gli itinerari disponibili",
                      "Trova un itinerario",
                      "Ho bisogno di un nuovo itinerario",
                      "Vorrei visualizzare un percorso",
                      "Mostrami un itinerario",
                      "Cerca un percorso specifico",
                      "Mi serve un itinerario per il mio viaggio",
                      "Come posso trovare un itinerario",
                      "Visualizza gli itinerari",
                      "Vorrei sapere quali itinerari ci sono",
                      "Cerca un percorso di viaggio",
                      "Fammi vedere gli itinerari disponibili",
                      "Aiutami a trovare un itinerario"]
    stop_examples = ['Ferma la ricerca',
                     'Stop ricerca',
                     'Stop']
    model_class : BaseModel = load_model()
    #model_class : BaseModel = Itinerary
    service = Service()
    limit = 3

    def __init__(self,cat):
        super().__init__(cat)
        self.last_message = len(self.cat.working_memory.history)-1
        

    def submit(self,form_model):
        prompt = """Il tuo compito è ringraziare l'utente per averti usato"""
        out = self.cat.llm(prompt)
        out = {}
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
                    prompt = f"""Il tuo compito è dire all'utente che non è stato trovato alcun risultato in base alle informazioni da lui fornite."""
                else:
                    prompt = f"""
                    Il tuo compito è quello di presentare all'utente i risultati della ricerca 
                    presenti nel seguente dizionario {results['hits']} escludendo il campo id e traducendo
                    il nome dei campi in italiano. Elenca ogni campo e il relativo valore nel seguente formato:
                    **nome_campo** : valore
                    E' importante inserire una spazio tra il campo e il due punti e tra il due punti e il valore
                    Infine chiedere se i risultati della ricerca vanno bene.
                    """
            except Exception as e:
                log.error(e)
                prompt = "Il tuo compito è quello di informare l'utente che la ricerca è fallita per un errore interno, invitalo a riprovare più tardi."    
        elif self._state == CatFormState.INCOMPLETE:
            if len(self._missing_fields) > 0:
                fields = self._missing_fields[0]
                log.info(self.model_class.model_fields)
                prompt = f"""Il tuo compito è quello di formulare una domanda all'utente in base alla seguente descrizione:
                  {self.model_class.model_fields[fields].description}. Tieni presente che stai aiutando l'utente a cercare un itinerario
                  dunque formula la domanda in modo pertinente."""
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
        history = []
        memory = self.cat.working_memory.history
        for mex in memory[self.last_message:]:
            if mex['who'] == 'Human' or ('risultati' not in mex['message'].lower() and mex['who'] == 'AI'):
                history.append(mex['message'])
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

This is the conversation, consider only messages where AI search results are not reported:
{history}
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