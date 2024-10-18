from cat.mad_hatter.decorators import hook,tool
from .service.baseservice import BaseService
from pydantic import BaseModel
from cat.log import log
import dataclasses 

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
    service_class = getattr(module,service)
    return service_class(**param)

def load_model() -> BaseModel:    
    module = importlib.import_module(config['model_module'])
    model = config['model_class']
    return getattr(module,model)

def method_state() -> dict:
     """"""
     return{
          
     }

def get_machine(cat):
    """"""
    getter_import = importlib.import_module(config['machine_getter_module'])
    getter = config['machine_getter']
    fun = getattr(getter_import,getter)
    return fun(cat)

from .finit_state_machine.automa import Automa

def get_automa(cat) -> Automa:
    module = importlib.import_module(config['automa_module'])
    classe = config['automa_class']
    automa = getattr(module,classe)
    return automa(cat)