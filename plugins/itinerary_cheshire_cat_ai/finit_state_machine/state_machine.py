from typing import Protocol
from automat import TypeMachine, TypeMachineBuilder
import dataclasses

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
    def confirm_result(self) -> dict:
        """Estrae la conferma e gestisce la prossima domanda"""
    def closed(self) -> dict:
        """Ringrazia l'utentee lo saluta"""

@dataclasses.dataclass
class CatDevices:
    cat : any

builder = TypeMachineBuilder(ChatBotController,CatDevices)
init = builder.state("init")
ask_adv = builder.state("ask_adv")
tell_adv = builder.state("tell_adv")
ask_step = builder.state("ask_step")
wait_conf_adv = builder.state("wait_conf_adv")
confirm = builder.state("confirm")
closed = builder.state("closed")

@init.upon(ChatBotController.init).loop()
def init_method(controller: ChatBotController,devices:CatDevices) -> dict:
    history = devices.cat.working_memory.history
    user_message = history[len(history)-1]['message']
    example_label = {
        "advice" : ["Dammi qualche suggerimento per un itinerario","Vorrei un itinerario basato sulle seguenti tappe"],
        "ask" : ["Vorrei creare un itinerario"]
    }
    classe = devices.cat.classify(user_message,labels=example_label)
    print(f"CLASS = {classe}")
    if classe == "advice":
        return {"callback" : controller.tell_advice}
    else:
        return {"callback" : controller.ask_advice}
    

@init.upon(ChatBotController.ask_advice).to(wait_conf_adv)
@confirm.upon(ChatBotController.ask_advice).to(wait_conf_adv)
def ask_advice_method(controller:ChatBotController,devices:CatDevices) -> dict:
    prompt = """Chiedi all'utente se vuole dare delle destinazioni iniziali oppure se vuole dei consigli"""
    out = devices.cat.llm(prompt)
    return {"output" : out, "next_state":wait_conf_adv.name}

@init.upon(ChatBotController.tell_advice).to(confirm)
@wait_conf_adv.upon(ChatBotController.tell_advice).to(confirm)
@confirm.upon(ChatBotController.tell_advice).to(confirm)
def tell_advice_method(controller:ChatBotController,devices:CatDevices) -> dict:
    #estrazione delle destinazioni già inserite dall'utente
    #ricerca di destinazioni utili
    #risposte
    print("OK")
    prompt = f"""Il tuo compito è presentare delle località calabresi sulla base dell'input dell'utente : 
    {devices.cat.working_memory.history[len(devices.cat.working_memory.history)-1]['message']}.
    Chiedere se i suggerimenti forniti vanno bene"""
    out = devices.cat.llm(prompt)
    return {"output":out,"next_state" : confirm.name}

@wait_conf_adv.upon(ChatBotController.wait_confirm_advice).loop()
def wait_confirm_advice_method(controller:ChatBotController,devices:CatDevices) -> dict:
    #estrazione della risposta dell'utente
    history = devices.cat.working_memory.history
    user_message = history[len(history)-1]['message']
    example_label = {
        "advice" : ["Vorrei un suggerimento","Vorrei un suggerimento basato sulle seguenti città"],
        "initial_dest" : ["No","Non voglio suggerimenti"]
    }
    classe = devices.cat.classify(user_message,labels=example_label)
    print(f"CLASS = {classe}")
    if classe == "initial_dest":
        return {"callback":controller.ask_step}
    else:
        return {"callback":controller.tell_advice}

@wait_conf_adv.upon(ChatBotController.ask_step).to(tell_adv)
def ask_step_method(controller:ChatBotController,devices:CatDevices) -> dict:
    prompt = """Chiedi all'utente quali destinazioni desidera avere nel suo itinerario"""
    out = devices.cat.llm(prompt)
    return {"output": out, "next_step" : tell_adv.name}

@confirm.upon(ChatBotController.confirm_result).loop()
def confirm_result_method(controller:ChatBotController,devices:CatDevices) -> dict:
    #estrai dall'ultimo messaggio se l'utente conferma i risultati
    history = devices.cat.working_memory.history
    user_message = history[len(history)-1]['message']
    example_label = {
        "closed" : ["si confermo"],
        "tell" : ["No dammi altri suggerimenti","No basati sulle seguenti tappe","Mi piacerebbe andare a"],
        "ask" : ["No"]
    }
    classe = devices.cat.classify(user_message,labels=example_label)
    print(f"CLASS = {classe}")
    if classe == "tell" :
        return {"callback":controller.tell_advice}
    elif classe == "ask" :
        return {"callback" : controller.ask_advice}
    else:
        return {"callback":controller.closed}

@confirm.upon(ChatBotController.closed).to(closed)
def closed_method(controller:ChatBotController,devices:CatDevices) -> dict:
    return {"output": ''}

machineFactory = builder.build()

def get_machine(cat) -> TypeMachine:
    return machineFactory(CatDevices(cat))
