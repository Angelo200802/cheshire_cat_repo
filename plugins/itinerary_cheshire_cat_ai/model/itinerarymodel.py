from pydantic import BaseModel, model_validator, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import requests 

class Categoria(Enum):
    PAESAGGISTICO = "paesaggistico"
    NATURALISTICO = "naturalistico"
    RELIGIOSO = "religioso"
    STORICO_CULTURALI = "storico culturali"

class Target(Enum):
    pass

class Itinerary(BaseModel):
    title: Optional[str] = Field(description="Titolo dell'itinerario",default="Titolo")
    category: Categoria = Field(description=f"la categoria dell'itinerario, i possibili valori sono {[cat for cat in Categoria]}")
    step: list[str] = Field(description="Lista di tappe dell'itinerario")
    #target: Target = Field(description="Target a cui è riferito l'itinerario")
    link: str = Field(description="link del sito a cui accedere per vedere l'itinerario")
    info : Optional[str] = Field(description="Informazioni del viaggio",default="")

    #@field_validator('link')
    #def check_link(cls, l):
    #    try:
    #        requests.head(l,allow_redirects=True, timeout=5)
    #        return l
    #    except requests.RequestException:
    #        raise ValueError("Il link specificato non è valido")

    @field_validator('category')
    def check_category(cls,c):
        if not c in Categoria:
            raise ValueError("La categoria non è valida.")
        return c