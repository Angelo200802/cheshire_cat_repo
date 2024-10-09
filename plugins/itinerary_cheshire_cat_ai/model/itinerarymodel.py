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
    STORICO_CULTURALI = "storico culturali"

class Step(BaseModel):
    country : str = Field()
    date_time : str = Field()
    description : str = Field()
    

class Itinerary(BaseModel):
    title: Optional[str] = Field(description="Titolo dell'itinerario",default="Titolo")
    step: list[str] = Field(description="Lista di tappe dell'itinerario")
    category: Categoria = Field(description=f"la categoria dell'itinerario, i possibili valori sono {[cat for cat in Categoria]}")
    link: str = Field(description="link del sito a cui accedere per vedere l'itinerario")
    info : Optional[str] = Field(description="Informazioni del viaggio",default="Nessuna informazione disponibile")

    #@field_validator('link')
    #def check_link(cls, l):
    #    try:
    #        res = requests.head(l)
    #        return l
    #    except requests.RequestException as e:
    #        log.error(f"ERRORE = {e}")
    #        raise ValueError("Il link specificato non è valido")

    @field_validator('category')
    def check_category(cls,c):
        if not c in Categoria:
            raise ValueError("La categoria non è valida.")
        return c