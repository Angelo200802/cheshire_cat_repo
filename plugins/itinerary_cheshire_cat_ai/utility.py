from cat.mad_hatter.decorators import hook
from .service.BaseService import BaseService
from pydantic import BaseModel
from cat.log import log

@hook
def agent_prompt_prefix(prefix,cat):
    settings = cat.mad_hatter.get_plugin().load_settings()
    prefix = settings['prefix']
    return prefix

import json
import importlib
import os 

config_path = "/home/angelo/progetto/plugins/itinerary_cheshire_cat_ai/config.json"
config = {}
with open(config_path, 'r') as file:
        config = json.load(file)
if not os.path.exists(config_path):
    print(f"Errore: il file di configurazione non esiste in {config_path}")
else:
     log.info("OK PATH TROVATO")
def load_service() -> BaseService:
    module = importlib.import_module(config['service_module'])
    service = config['service_class']
    param = config.get('service_param',{})
    model = load_model()
    service_class = getattr(module,service)
    param['model_class'] = model
    return service_class(**param)

def load_model() -> BaseModel:    
    module = importlib.import_module(config['model_module'])
    model = config['model_class']
    return getattr(module,model)