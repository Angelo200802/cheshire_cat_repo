from typing import Protocol
from automat import TypeMachine, TypeMachineBuilder
import dataclasses

class ChatBotController(Protocol):
    def init(self) :
        """Inizializza lo stato"""
    def ask_advice(self) -> dict:
        """Chiede all'utente se vuole un suggerimento"""
    def wait_decision(self) -> dict:
        """Aspetta di ricevere l'input sul suggerimento dall'utente"""
    def ask_step(self) -> dict:
        """Chiede all'utente che destinazioni vuole aggiugere all'itinerario"""
    def wait_response_step(self) -> dict:
        """Aspetta che l'utente gli dia la destinazione"""
    def tell_advice(self) -> dict:
        """Espone all'utente i suggerimenti"""
    def wait_response_advice(self) -> dict:
        """"""
    def confirm_end(self) -> dict:
        """Chiede all'utente la conferma dell'itinerario"""
    def wait_confirm(self) -> dict:
        """"""
    def closed(self) -> dict:
        """Ringranzia l'utente per l'utilizzo"""

@dataclasses.dataclass
class CatDevices:
    cat : any

dest = ['Cosenza','Catanzaro','Crotone']
builder = TypeMachineBuilder(ChatBotController,CatDevices)
init = builder.state("init")
ask_advice = builder.state("ask_advice")
advicing = builder.state("advicing")
wait_decision = builder.state("wait_decision")
step = builder.state("step")
wait_step = builder.state("wait_step")
wait_advice = builder.state("wait_advice")
confirm = builder.state("confirm")
wait_confirm = builder.state("wait_confirm")
closed = builder.state("closed")

@init.upon(ChatBotController.init).loop()
def init_method(controller: ChatBotController,devices:CatDevices):
    history = devices.cat.working_memory.history
    user_message = history[len(history)-1]['message']
    example_label = {
        'advice' : ["Dammi qualche suggerimento per un itinerario"],
        'boot' : ["Vorrei creare un itinerario"],
        'add' : ["Aggiungi al mio itinerario le seguenti tappe"]
    }
    classe = devices.cat.classify(user_message,labels=example_label)
    print(f"CLASS = {classe}")
    if classe == 'boot':
        return controller.ask_advice()
    elif classe == 'advice' :
        return controller.tell_advice()
    else:
        return controller.confirm_end()

@init.upon(ChatBotController.ask_advice).to(wait_decision)
def ask_advice_method(controller:ChatBotController,devices:CatDevices) -> dict:
    prompt = """Il tuo compito è chiedere all'utente se ha già in mente delle destinazioni oppure se vuole qualche suggerimento"""
    out = devices.cat.llm(prompt)
    return {"output":out, "next_state":wait_decision.name}

@wait_decision.upon(ChatBotController.wait_decision).loop()
def decision_method(controller:ChatBotController,devices:CatDevices) -> dict:
    history = devices.cat.working_memory.history
    user_message = history[len(history)-1]['message']
    example_label = {
        "True" : ["Vorrei un suggerimento"],
        "False" : ["Ho già in mente le mie tappe"]
    }
    _class = devices.cat.classify(user_message,labels=example_label)
    if _class == "True":
        return controller.tell_advice()
    else :
        return controller.ask_step()

@init.upon(ChatBotController.tell_advice).to(confirm)
@wait_decision.upon(ChatBotController.tell_advice).to(confirm)
def tell_advice_method(controller:ChatBotController,devices:CatDevices) -> dict:
    #Logica di estrazione delle destinazioni
    prompt = f"""Il tuo compito è suggerire all'utente le seguenti destinazioni : {dest}"""
    out = devices.cat.llm(prompt)
    return {"output":out,"next_state":confirm}

@init.upon(ChatBotController.confirm_end).to(wait_confirm)
def confirm_end_method(controller:ChatBotController,devices:CatDevices) -> dict:
    prompt = f"""Il tuo compito è ripielogare le seguenti destinazioni all'utente: {dest}.
                Chiedi all'utente se è soddisfatto delle destinazioni scelte"""
    out = devices.cat(prompt)
    return {"output":out,"next_state":wait_confirm}

machineFactory = builder.build()

def get_machine(cat) -> TypeMachine:
    return machineFactory(CatDevices(cat))


    