from typing import Protocol
from automat import TypeMachine, TypeMachineBuilder
import dataclasses
from ..utility import load_service, get_random_places, luoghi_da_visitare, get_json
import json

class ChatBotController(Protocol):
    def init(self) -> dict :
        """Inizializza lo stato"""
    def ask_advice(self) -> dict:
        """Chiede all'utente se vuole un suggerimento"""
    def wait_confirm_advice(self) -> dict:
        """Aspetta la risposta dell'utente in merito ai consigli"""
    def tell_advice(self) -> dict:
        """Espone all'utente i risultati della ricerca, estrae come parametri delle tappe già presentate dall'utente"""
    def ask_step(self) -> dict:
        """Chiede all'utente delle destinazioni su cui basare i propri consigli"""
    def step_ok(self) -> dict:
        """Verifica che le destinazioni inserite siano ok"""
    def confirm_result(self) -> dict:
        """Estrae la conferma e gestisce la prossima domanda"""
    def closed(self) -> dict:
        """Ringrazia l'utente lo saluta"""

@dataclasses.dataclass
class CatDevices:
    cat : any

service = load_service()

stop_examples = ["stop","fermati","non voglio continuare"]

builder = TypeMachineBuilder(ChatBotController,CatDevices)
init = builder.state("init")
ask_adv = builder.state("ask_adv")
tell_adv = builder.state("tell_adv")
ask_step = builder.state("ask_step")
wait_conf_adv = builder.state("wait_conf_adv")
confirm = builder.state("confirm")
step_ok = builder.state("step_ok")
closed = builder.state("closed")

@init.upon(ChatBotController.init).loop()
def init_method(controller: ChatBotController,devices:CatDevices) -> dict:
    history = devices.cat.working_memory.history
    user_message = history[len(history)-1]['message']
    prompt = f"""Considera il seguente messaggio : "{user_message}.
    Restituisci un json nel seguente formato:
    {{ 
        "label": valore 
    }} 
    Dove valore è uno delle seguenti etichette:
    "adv" se nel messaggio viene chiesto un suggerimento su un itinerario, 
    "step" se nel messaggio si chiede di creare un itinerario basato su delle tappe,
    "ask" se il messaggio non specifica un suggerimento oppure se non sono presenti tappe specificate."""
    classe = get_json(devices.cat,prompt)['label']
    if classe == "adv" or classe == "step":
        if classe == "step" and not verify_destination_is_present(devices.cat):
            return {"callback": controller.ask_step}
        return {"callback" : controller.tell_advice}
    else:
        return {"callback" : controller.ask_advice}
    

@init.upon(ChatBotController.ask_advice).to(wait_conf_adv)
@confirm.upon(ChatBotController.ask_advice).to(wait_conf_adv)
def ask_advice_method(controller:ChatBotController,devices:CatDevices) -> dict:
    prompt = """Chiedi all'utente se vuole dare delle destinazioni iniziali oppure se vuole dei consigli"""
    out = devices.cat.llm(prompt)
    return {"output" : f"""{{"mex" : "{out}"}}""", "next_state":wait_conf_adv.name}

@init.upon(ChatBotController.tell_advice).to(confirm)
@wait_conf_adv.upon(ChatBotController.tell_advice).to(confirm)
@confirm.upon(ChatBotController.tell_advice).to(confirm)
@step_ok.upon(ChatBotController.tell_advice).to(confirm)
def tell_advice_method(controller:ChatBotController,devices:CatDevices) -> dict:
    prompt = f"""Converti il seguente dialogo: {devices.cat.working_memory.history} in un json con il seguente formato:
        {{
            destinazioni : {{ index : nome_destinazione }}
        }}
        Dunque estrai le destinazioni dalla conversazione, se nessuna destinazione viene specificata la lista deve
        essere vuota.
    """
    dest = get_json(devices.cat,prompt)['destinazioni']
    if len(dest) == 0:
        dest = get_random_places(3)
    print(dest)
    results = {}
    i = 0
    for d in dest:
        data = luoghi_da_visitare(dest[d],2)
        for place in data:
            results[i] = place
            i += 1
    prompt = f"""Presenta i seguenti risultati di un itinerario generando un json nel seguente formato:
    {{
        "mex" : messaggio
        "results" : {results} 
    }}
    Dove messaggio nel campo "mex" è un testo introduttivo che presenta "results", e che deve chiedere all'utente se desidera confermare 
    l'itinerario
    """
    out = get_json(devices.cat, prompt)
    return {"output":f"""{out}""","next_state" : confirm.name}

@wait_conf_adv.upon(ChatBotController.wait_confirm_advice).loop()
def wait_confirm_advice_method(controller:ChatBotController,devices:CatDevices) -> dict:
    history = devices.cat.working_memory.history
    user_message = history[len(history)-1]['message']
    prompt = f"""Considera il seguente messaggio : {user_message}.
    Restituisci un json con il seguente formato: 
    {{
        "label" : valore
    }}
    Dove valore è una delle seguenti etichette:
    "adv" se nel messaggio si sta chiedendo un suggerimento,
    "exit" se il messaggio è simile uno dei seguenti valori : {stop_examples},
    "dest" se nel messaggio viene detto che si vuole basare l'itinerario su delle tappe
    """
    classe = get_json(devices.cat,prompt)['label']
    if classe == "adv" or classe == "dest":
        if classe == "dest" and not verify_destination_is_present(devices.cat):
            return {"callback" : controller.ask_step}
        return {"callback":controller.tell_advice}
    else:
        return {"callback" : controller.closed}

@wait_conf_adv.upon(ChatBotController.ask_step).to(step_ok)
@confirm.upon(ChatBotController.ask_step).to(step_ok)
@init.upon(ChatBotController.ask_step).to(step_ok)
def ask_step_method(controller:ChatBotController,devices:CatDevices) -> dict:
    prompt = """Chiedi all'utente quali destinazioni desidera avere nel suo itinerario"""
    out = devices.cat.llm(prompt)
    return {"output": f"""{{"mex" : "{out}"}}""", "next_state" : step_ok.name}

@step_ok.upon(ChatBotController.step_ok).loop()
def step_ok_method(controller:ChatBotController,devices:CatDevices) -> dict:
    history = devices.cat.working_memory.history
    user_message = history[len(history)-1]['message']
    prompt = f"""Considera il seguente messaggio : {user_message}.
    Restituisci un json nel seguente formato:
    {{
        "label" : valore
    }}
    Dove valore è uno delle seguenti etichette:
    "exit" se il messaggio è simile a uno dei valori presenti nella seguente lista: {stop_examples},
    "adv" se nel messaggio si sta chiedendo un suggerimento,
    "step" se nel messaggio si fa riferimento ad un elenco di tappe/destinazioni di un itinerario
    """ 
    classe = get_json(devices.cat,prompt)['label']
    if classe == "exit":
        return {"callback" : controller.closed }
    elif classe == "adv":
        return { "callback" : controller.tell_advice }
    else :
        if not verify_destination_is_present(devices.cat):
            return {"callback" : controller.ask_step}
        return {"callback" : controller.tell_advice}
    

@confirm.upon(ChatBotController.confirm_result).loop()
def confirm_result_method(controller:ChatBotController,devices:CatDevices) -> dict:
    history = devices.cat.working_memory.history
    user_message = history[len(history)-1]['message']
    prompt = f"""Considera il seguente messaggio: {user_message}.
    Restituisci un json nel seguente formato:
    {{  
        "label" : valore
    }}
    Dove valore è una delle seguenti etichette:
    "close" se il messaggio è positivo come "si va bene",
    "exit" se il messaggio è simile ad uno dei valori della seguente lista : {stop_examples},
    "step" se il messaggio fa riferimento a delle tappe/destinazioni di un itinerario,
    "adv" se il messaggio è negativo e/o viene chiesto un altro suggerimento
    """
    classe = get_json(devices.cat,prompt)['label']
    if classe == "exit" or classe == "close":
        return {"callback" : controller.closed }
    elif classe == "step":
        if not verify_destination_is_present(devices.cat):
            return {"callback" : controller.ask_step}
    return {"callback" : controller.tell_advice }
    

@confirm.upon(ChatBotController.closed).to(closed)
@init.upon(ChatBotController.closed).to(closed)
@wait_conf_adv.upon(ChatBotController.closed).to(closed)
@step_ok.upon(ChatBotController.closed).to(closed)
def closed_method(controller:ChatBotController,devices:CatDevices) -> dict:
    prompt = f"""Il tuo compito è ringraziare l'utente per averti usato e invitalo a usarti nuovamente."""
    out = devices.cat.llm(prompt)
    return {"output": f"""{{"mex" : "{out}"}}""", "next_state" : closed.name}

def verify_destination_is_present(cat) -> bool:
    history = cat.working_memory.history
    mex = history[len(history)-1]['message']
    prompt = f"""Considera il seguente messaggio: "{mex}". 
            Restituisci un json con la seguente struttura: {{ "present" : true se è presente almeno una località, false altrimenti }}    
            """
    step = cat.llm(prompt)
    return 'true' in step.lower()


machineFactory = builder.build()
def get_machine(cat) -> TypeMachine:
    return machineFactory(CatDevices(cat))