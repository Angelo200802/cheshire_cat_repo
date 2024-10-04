from cat.mad_hatter.decorators import hook,tool
import requests
import random

@hook
def agent_prompt_prefix(prefix,cat):
	print("Lista di job: \n"+str(cat.white_rabbit.get_jobs()))
	settings = cat.mad_hatter.get_plugin().load_settings()
	prefix = settings['prefix']
	return prefix
@hook
def agent_prompt_suffix(suffix,cat):
	settings = cat.mad_hatter.get_plugin().load_settings()
	suffix = settings['suffix']
	return suffix
@hook("before_cat_reads_message")
def command(user_input,cat):
	if user_input.text.startswith('/'):
		com = user_input.text[1:].strip()
		if com == 'help':
			user_input.text = 'Hey ho bisogno di aiuto!'
		if com == 'greet':
			user_input.text = 'Ciao!!!'
		if com == 'meteo':
			user_input.text = "Mi dici il meteo di oggi a Cosenza?"
	return user_input

@hook
def agent_fast_reply(fast_reply,cat):
	if cat.working_memory.recall_query == "/gioco":
		fast_reply['output'] = "Dimmi un numero da 1 a 10"
	return fast_reply
@hook("before_cat_sends_message")
def greet_mex(data,cat):
	if 'ciao' in data.content.lower() :
		data.content = f"Ciao!!!"
	return data 

@tool(return_direct=True)
def get_meteo(city,cat):
	""" Useful to know the weather. City is the input"""
	url = f"https://www.metaweather.com/api/location/search/?query={city}"
	response = requests.get(url)
	response.raise_for_status()
	return response.text

#@tool(return_direct=True)
def numero(num,cat):
	"""To use when the user send only a number.
	"""
	random_number = random.randint(1,10)
	if random_number == int(num):
		cat.send_ws_message("Hai vinto")
		return f"Bravo stavo pensando proprio a {num}"
	else:
		cat.send_ws_message(f"Hai perso")
		return f"Ops sbagliato, non stavo pensando a {num} ma a {random_number}"
