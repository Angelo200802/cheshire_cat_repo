import os
import asyncio
import logging
import json 

from typing import Dict

from telegram import Update, Bot
from telegram.ext import Application, ApplicationBuilder, ApplicationHandlerStop, ContextTypes, CommandHandler, MessageHandler ,filters
from telegram.constants import ChatAction

from .cat_conn import Connection

#LISTA DI COMANDI
COMMAND = {
    "/sign" : "Usalo se devi registrare un tuo itinerario",
    "/search" : "Usalo se devi cercare un itinerario",
    "/stop" : "Ferma l'attività che stai facendo"
}


class Telegram:
    
    def __init__(self,token,cc_url,cc_port):
        self.cc_url = cc_url
        self.cc_port = cc_port
        self.last_typing_action = {}
        #MONITORA GLI EVENTI E LI GESTISCE
        self._loop = asyncio.get_running_loop()
        #COSA PER LO SCAMBIO DI DATI TRA COREROUTINE
        self._out_queue = asyncio.Queue()
        #DIZIONARIO DI CONNESSIONI APERTE
        self._connections : Dict[str,Connection] = {}
        #APPLICAZIONE TELEGRAM
        self.telegram = ApplicationBuilder().token(token).build()
        self.bot = self.telegram.bot
        #COMMAND HANDLER => GESTIONE DEI COMANDI INVIATI NELLA CHAT
        self.telegram.add_handler(CommandHandler("help",self.help_command)) #FORNISCE LA LISTA DI COMANDI
        self.telegram.add_handler(CommandHandler("search",self.search)) #AVVIA IL FORM DI RICERCA ITINERARI
        self.telegram.add_handler(CommandHandler("sign",self.sign)) #AVVIA IL FORM DI REGISTRAZIONE DI ITINERARI
        #MESSAGE HANDLER => GESTIONE DEI MESSAGGI TESTUALI / FOTO / ETC
        connect_handler = MessageHandler(filters.ALL, self._open_connection)
        self.telegram.add_handler(connect_handler) #APERTURA DELLA CONNESSIONE SE NON ESISTE
        text_message_handler = MessageHandler(filters.TEXT,self._text_handler)
        self.telegram.add_handler(text_message_handler) #GESTIONE DEI MESSAGGI DA INOLTRARE AL CHESHIRE CAT
    
        
    async def search(self,update:Update,context:ContextTypes.DEFAULT_TYPE):
        await self._text_handler(update,context,"Vorrei trovare un itinerario")

    async def sign(self,update:Update,context:ContextTypes.DEFAULT_TYPE):
        await self._text_handler(update,context,"Vorrei cercare un itinerario")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        command_list = ""
        for com in COMMAND:
            command_list += f"{com} : {COMMAND[com]}\n"
        await update.message.reply_text(f"Ciao, puoi scegliere tra i seguenti comandi:\n {command_list}")
    
    async def _open_connection(self,update:Update,context:ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id

        if chat_id not in self._connections: #SE NON ESISTE CREA LA CONNESSIONE
            self._connections[chat_id] = Connection(chat_id,self._out_queue,self.cc_url,self.cc_port)
        
        if not self._connections[chat_id].is_connected:
            await self._connections[chat_id].connect() #SE NON CONNESSO ASPETTA LA CONNESSIONE
            if not self._connections[chat_id].is_connected: #SE LA CONNESSIONE FALLISCE LANCIA L'ECCEZIONE
                logging.warning("Connessione fallita")
                raise ApplicationHandlerStop
        
    async def _text_handler(self,update:Update,context:ContextTypes.DEFAULT_TYPE,message:str):
        pass
    async def run(self):
        try:
            await self.telegram.initialize() #INIZIALIZZAZIONE DEL BOT
            await self.telegram.updater.start_polling(read_timeout=10) #MONITORA E RICEVE I MESSAGGI DAI SERVER TELEGRAM
            await self.telegram.start() #AVVIA IL BOT PER RICEVERE ED ELABORARE I MESSAGGI
            await self._loop.create_task(self._out_queue_dispatcher()) #AVVIA LA COREROUTINE
        except asyncio.CancelledError:
            logging.info("STOP")
            await self.telegram.updater.stop()
            await self.telegram.stop()
    
    async def _out_queue_dispatcher(self): #DISPATCHA I MESSAGGI AI DESTINATARI - USATO DALL'EVENT LOOPER
        while True:
            mex, id = await self._out_queue.get()
            logging.debug(f"Message from {id}: {json.dumps(mex,indent=4)}")

            try:
                if mex['type'] == 'chat':
                    await self._dispatch_chat_message(mex,id)
                elif mex['type'] == 'chat_token':
                    await self._dispatch_chat_token(id)
            except Exception as e:
                logging.error(f"Si è verificato un errore: {e}")

    async def _dispatch_chat_message(self,mex,id):
        send_params = mex.get("meowgram", {}).get("send_params", {})
        
        await self.bot.send_message(
            chat_id=id,
            text=mex['content'],
            **send_params 
        )

    async def _dispatch_chat_token(self, user_id):
        import time
        t = time.time()

        if user_id not in self.last_typing_action:
            self.last_typing_action[user_id] = t - 5
        if t - self.last_typing_action[user_id] > 5:
            logging.info(f"Sending chat action Typing to user {user_id}")
            self.last_typing_action[user_id] = t

            await self.bot.send_chat_action(
                chat_id=user_id,
                action=ChatAction.TYPING
            )