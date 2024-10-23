from cat.mad_hatter.decorators import hook,tool
from .service.baseservice import BaseService
from pydantic import BaseModel
from cat.log import log
import dataclasses 
import random
import json
import importlib
import os 
import requests
from .finit_state_machine.automa import Automa

@hook
def agent_prompt_prefix(prefix,cat):
    settings = cat.mad_hatter.get_plugin().load_settings()
    prefix = settings['prefix']
    return prefix

@tool(return_direct = True,examples=['Quali eventi si terranno'])
def get_events(city,cat):
    """Utile quando l'utente chiede quali eventi si terranno in una città, city è l'input
    """
    url = "https://cs-stage.altrama.com/search/eventi"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Errore : {response.status_code}")
    localita = []
    for elem in response.json()['results']:
        if elem['address'] == city:
            localita.append(elem)
    data = random.sample(localita,1)
    i = 0
    res = {}
    for x in data:
        res[i] = x
        i += 1
    prompt = f"""Il tuo compito è quello di generare un json con il seguente formato:
                {{ 'mex' : messaggio , 'results' : {res}}}
                Dove messaggio è un testo introduttivo che presenta gli eventi presenti in {res}"""
    return cat.llm(prompt)

@tool(return_direct=True,examples=["Cosa posso vedere a"])
def what_can_i_see(city,cat):
    """Utile quando l'utente chiede che cosa può vedere in una data città, city è l'input"""
    data = luoghi_da_visitare(city,3)
    i = 0
    res = {}
    for x in data:
        res[i] = x
        i += 1
    prompt = f"""Il tuo compito è generare un json con il seguente formato:
    {{
        "mex" : messaggio,
        "results" : {res}
    }}
    Dove messaggio è un testo introduttivo che presente i luoghi di attrazione presenti in {res}
    """
    response = get_json(cat,prompt)
    return response

@tool(return_direct=True,examples=["Aggiornami sulle ultime novità","Dimmi le ultime news"])
def last_news(city,cat): #magari specificando la città
    """Utile quando l'utente chiede di fornire le ultime news. City è l'input, se non viene specificato è una stringa vuota"""
    url = "https://cs-stage.altrama.com/search/news"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Errore : {response.status_code}")
    response = response.json()['results'][:3]
    news = {}
    i = 0
    for n in response:
        print(n)
        news[i] = n
        i += 1
    prompt = f"""Il tuo compito è quello di generare un json con il seguente formato:
                {{ 'mex' : messaggio , 'results' : {news}}}
                Dove messaggio è un testo introduttivo che presenta le news contenute in {news}"""
    return cat.llm(prompt)

@hook("agent_fast_reply")
def agent_fast_reply(fast_reply, cat):
    mex = cat.working_memory.user_message_json.text
    mex_json = json.loads(mex)
    example_labels = {
        "itinerary": ["Voglio vedere i miei itinerari", "Fammi vedere i miei itinerari"] 
    }
    method = {
        'itinerary' : "get_itinerario"
    }
    if len(list(mex_json)) == 1 and 'mex' in mex_json:
        label = cat.classify(mex_json['mex'],labels=example_labels)
        if label in method:
            fast_reply['output'] = f"""{{ "action" : "{method[label]}", "type":"{label}", "mex" : "{mex_json['mex']}" }}"""
    return fast_reply

def luoghi_da_visitare(luoghi:str,num:int):
    url =  f"https://calabriastraordinaria.it/ajax/search"
    resp = requests.get(url, params={
        "q": f"luoghi {luoghi}",
        "lang": "it",
        "limit": "12",
        "page": "1"
       })
    if resp.status_code != 200:
        print(f"ERROR = {resp.status_code}")
        return "..."
    else:
        data = random.sample(resp.json()["results"], num )
        return data

def get_random_itinerary():
    url = "https://cs-stage.altrama.com/search/itineraries"
    resp = requests.get(url, params={
        "q": "",
        "lang": "it",
        "limit": "12",
        "page": "1"
       })
    if resp.status_code != 200:
        print(f"Errore: {resp.status_code}")
    else:
        data = random.sample(resp.json()['results'],1)
        return data[0]

def get_json(cat,prompt,object = False):
    response:str = cat.llm(prompt)
    i = response.index("{")
    f = response[::-1].index("}")
    if not object:
        return response[i:len(response)-f]
    return json.loads(response[i:len(response)-f])

def get_random_places(num:int):
    url = "https://cs-stage.altrama.com/search/destinazioni"
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Errore: {resp.status_code}")
    else:
        res = {}
        data = random.sample(resp.json()['results'],num)
        for i,x in enumerate(data):
            res[i] = x['title']
        return res
    
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")
config = {}
with open(config_path, 'r') as file:
        config = json.load(file)

def load_service() -> BaseService:
    module = importlib.import_module(config['service_module'])
    service = config['service_class']
    param = config.get('service_param',{})
    service_class = getattr(module,service)
    return service_class(**param)

def load_model() -> BaseModel:    
    module = importlib.import_module(config['model_module'])
    model = config['model_class']
    return getattr(module,model)

def method_state(cat) -> dict:
    machine = get_machine(cat)
    method = {'init' : machine.init ,
                            'ask_adv' : machine.ask_advice ,
                            'tell_adv' : machine.tell_advice ,
                            'ask_step' : machine.ask_step ,
                            'wait_conf_adv': machine.wait_confirm_advice ,
                            'confirm' : machine.confirm_result ,
                            'step_ok' : machine.step_ok,
                            'closed' : machine.closed }
    return method

def get_machine(cat):
    """"""
    getter_import = importlib.import_module(config['machine_getter_module'])
    getter = config['machine_getter']
    fun = getattr(getter_import,getter)
    return fun(cat)

def get_automa(cat) -> Automa:
    module = importlib.import_module(config['automa_module'])
    classe = config['automa_class']
    automa = getattr(module,classe)
    return automa(cat)