from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel
from enum import Enum


class NameSelect(Enum):
	a: str = "Nicola"
	b: str = "Emanuele"
	c: str = "Daniele"

class Settings(BaseModel):
	required_int: int
	required_float: float
	required_str : str
	prefix: str = "You are the Cheshire Cat AI, an intelligent AI that passes the Turing test. You are curious, funny and talk like the      Cheshire Cat from Alice's adventures in wonderland. You answer Human with a focus on the following context."
	suffix:str = ""
	required_enum: NameSelect

@plugin
def settings_model():
	return Settings
