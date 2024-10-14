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

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")
config = {}
with open(config_path, 'r') as file:
        config = json.load(file)

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