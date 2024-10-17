from typing import Protocol
from automat import TypeMachine, TypeMachineBuilder
import dataclasses
from ..utility import load_service
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
    example_label = {
        "advice" : ["Dammi qualche suggerimento per un itinerario","Hai qualche proposta per un viaggio?",
                    "Mi daresti qualche idea per un percorso da seguire?","Quali luoghi mi consiglieresti di visitare?",
                    "suggeriscimi un itinerario","Puoi consigliarmi un itinerario?",
                    "Vorrei sapere se hai suggerimenti per un itinerario interessante","Puoi suggerirmi un percorso da esplorare?",
                    "Hai qualche raccomandazione per un itinerario?","Mi servirebbero consigli su dove andare durante il viaggio",
                    "Quali attrazioni dovrei includere nel mio itinerario?"],
        "ask" : ["Vorrei creare un itinerario","Mi piacerebbe pianificare un itinerario.","Ho intenzione di organizzare un percorso di viaggio.",
                "Voglio mettere insieme un itinerario.","Desidero strutturare un itinerario.","Sto pensando di creare un percorso di viaggio.",
                "Vorrei progettare un itinerario.","Mi interessa elaborare un itinerario.","Voglio definire un percorso per il mio viaggio.",
                "Ho bisogno di preparare un itinerario.","Sto cercando di costruire un percorso di viaggio."],
        "telling" : ["Organizza un itinerario utilizzando queste tappe.","Pianifica un percorso considerando le seguenti destinazioni."
                    "Metti insieme un itinerario partendo da queste tappe.","Sviluppa un itinerario basato sui luoghi indicati."
                    ,"Costruisci un percorso utilizzando le seguenti tappe.","Elabora un itinerario tenendo conto di queste destinazioni.",
                    "Progetta un percorso seguendo le tappe elencate.","Imposta un itinerario considerando le seguenti località.",
                    "Definisci un percorso basato su queste tappe.","Crea un tragitto seguendo le destinazioni indicate."]
    }
    classe = devices.cat.classify(user_message,labels=example_label)
    print(f"CLASS = {classe}")
    if classe == "advice" or classe == "telling":
        if classe == "telling":
            okay = verify_destination_is_present(devices.cat)
            if not okay:
                return {"callback": controller.ask_step}
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
    prompt = f"""Converti il seguente dialogo: {devices.cat.working_memory.history} in un json con il seguente formato:
        {{
            destinazioni : {{ index : nome_destinazione}}
        }}
        Dunque estrai le destinazioni dalla conversazione, se nessuna destinazione viene specificata la lista deve
        essere vuota.
    """
    dest : str = devices.cat.llm(prompt)
    i = dest.index('{')
    f = dest[::-1].index("}")
    dest = dest[i:len(dest)-f]
    print(f"DEST = {dest}")
    dest = json.loads(dest)
    if len(dest['destinazioni']) == 0:
        #Cerca le destinazioni migliori e correlate e presentale
        results = service.search('',5)
        prompt = f"""Il tuo compito è presentare le seguenti località: {results}. Chiedere se l'itinerario fornito va bene"""
    else:
        query = ""#crea la query in base alle destinazioni
        results = service.search(query,5)
        prompt = f"""Il tuo compito è presentare le seguenti località : {results}.
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

@wait_conf_adv.upon(ChatBotController.ask_step).to(step_ok)
@init.upon(ChatBotController.ask_step).to(step_ok)
@confirm.upon(ChatBotController.ask_step).to(step_ok)
def ask_step_method(controller:ChatBotController,devices:CatDevices) -> dict:
    prompt = """Chiedi all'utente quali destinazioni desidera avere nel suo itinerario"""
    out = devices.cat.llm(prompt)
    print(step_ok.name)
    return {"output": out, "next_step" : step_ok.name}

@step_ok.upon(ChatBotController.step_ok).loop()
def step_ok_method(controller:ChatBotController,devices:CatDevices) -> dict:
    okay = verify_destination_is_present(devices.cat)
    if okay :
        return {"callback":controller.tell_advice}
    else:
        return {"callback" : controller.ask_step }

@confirm.upon(ChatBotController.confirm_result).loop()
def confirm_result_method(controller:ChatBotController,devices:CatDevices) -> dict:
    #estrai dall'ultimo messaggio se l'utente conferma i risultati
    history = devices.cat.working_memory.history
    user_message = history[len(history)-1]['message']
    example_label = {
        "closed" : ["si confermo","si","okay","va bene"],
        "tell" : ["No, vorrei altri consigli.","No, fammi altre proposte.","No, suggeriscimi qualcos'altro",
                "No, dammi qualche altro consiglio.","No, preferisco altre opzioni.","No, mostrami altri suggerimenti.",
                "No, vorrei più alternative.","No, ho bisogno di altri spunti.","No, proponi qualcos'altro.","No, suggerisci altre idee.",
                "No, considera le seguenti tappe.","No, utilizza queste destinazioni come riferimento.","No, basati su queste località.",
                "No, tieni conto delle tappe indicate.","No, prendi in considerazione questi luoghi.","No, segui queste destinazioni.",
                "No, usa queste tappe come base.","No, parti dalle località elencate.","No, organizza il tutto seguendo queste tappe.",
                "No, concentrati sulle seguenti destinazioni."],
        "ask" : ["No","non vanno bene"]
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

def verify_destination_is_present(cat) -> bool:
    history = cat.working_memory.history
    mex = history[len(history)-1]['message']
    prompt = f"""Considera il seguente messaggio: {mex}. Rispondi con true se il messaggio contiene un elenco con almeno una
            destinazione, false altrimenti"""
    step = cat.llm(prompt)
    return 'true' in step.lower()

machineFactory = builder.build()

def get_machine(cat) -> TypeMachine:
    return machineFactory(CatDevices(cat))
