from typing import Protocol
from automat import TypeMachine, TypeMachineBuilder
import dataclasses

class ChatBotController(Protocol):
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

builder = TypeMachineBuilder(ChatBotController,CatDevices)
init = builder.state("init")
advicing = builder.state("advicing")
wait_decision = builder.state("wait_decision")
step = builder.state("step")
wait_step = builder.state("wait_step")
wait_advice = builder.state("wait_advice")
confirm = builder.state("confirm")
wait_confirm = builder.state("wait_confirm")
closed = builder.state("closed")

@init.upon(ChatBotController.ask_advice).to(wait_decision)
def metod(controller: ChatBotController,devices:CatDevices) -> dict:
    prompt = """Il tuo compito è quello di chiedere all'utente se ha in mente qualche destinazione 
                oppure se ha bisogno di un consiglio per il suo itinerario"""
    out = devices.cat.llm(prompt)
    return {"output":out, "next_state" : wait_decision.name}
@wait_decision.upon(ChatBotController.wait_decision).loop()
def metod(controller: ChatBotController,devices:CatDevices) -> dict:
    return {"output":"Ok queste sono le tappe suggerite"}
@advicing.upon(ChatBotController.tell_advice).to(wait_advice)
def metod(controller: ChatBotController, devices:CatDevices) -> dict:
    pass

machineFactory = builder.build()

def get_machine(cat) -> TypeMachine:
    return machineFactory(CatDevices(cat))

machine = get_machine(None)
print(dir(machine))
    