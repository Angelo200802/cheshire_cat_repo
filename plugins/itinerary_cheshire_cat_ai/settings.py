from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel
from enum import Enum

class SelectLanguage(Enum):
    a : str = "Italian"
    b : str = "English"

class Settings(BaseModel):
    prefix : str = "You are the Cheshire Cat AI, an intelligent AI that passes the Turing test. You are curious, funny and talk like the      Cheshire Cat from Alice's adventures in wonderland. You answer Human with a focus on the following context."
    language : SelectLanguage = SelectLanguage.b

@plugin
def settings_model():
	return Settings