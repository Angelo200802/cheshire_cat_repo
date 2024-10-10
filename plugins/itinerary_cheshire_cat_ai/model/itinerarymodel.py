from pydantic import BaseModel, model_validator, Field, field_validator
from typing import Optional
from enum import Enum
import requests 
from datetime import datetime
from cat.log import log

class Categoria(Enum):
    PAESAGGISTICO = "paesaggistico"
    NATURALISTICO = "naturalistico"
    RELIGIOSO = "religioso"
    STORICO_CULTURALE = "storico culturale"

class Target(Enum):
    FAMIGLIA = "famiglia"
    COPPIA = "coppia"
    SOLITARIO = "solitario"
    GRUPPO = "gruppo"
    PER_TUTTI = "per tutti"

class Step(BaseModel):
    country : str = Field()
    date_time : str = Field()
    description : str = Field()
    

class Itinerary(BaseModel):
    step: list[str] = Field(description="Elenco di tappe dell'itinerario")
    target: Target = Field(description=f"Target a cui è rivolto l'itinerario, i possibili valori sono {[tg for tg in Target]}")
    category: Categoria = Field(description=f"la categoria dell'itinerario, i possibili valori sono {[cat for cat in Categoria]}")
    title: str = Field(description="Titolo dell'itinerario")
    link: Optional[str] = Field(description="link del sito a cui accedere per vedere l'itinerario",default="")
    info : Optional[str] = Field(description="Informazioni del viaggio",default="Nessuna informazione disponibile")

    #@field_validator('link')
    #def check_link(cls, l):
    #    if l == "":
    #        return l
    #    try:
    #        res = requests.head(l)
    #        return l
    #    except requests.RequestException as e:
    #        log.error(f"ERRORE = {e}")
    #        raise ValueError("Il link da te inserito non è valido")

    @field_validator('category')
    def check_category(cls,c):
        if not c in Categoria:
            raise ValueError("La categoria da te inserita non è valida.")
        return c