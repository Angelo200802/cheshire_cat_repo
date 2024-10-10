import os 
import logging
import asyncio

from dotenv import load_dotenv
from colorlog import ColoredFormatter

from .telegram_int import Telegram

load_dotenv()
#IMPORTA IL BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")
#IMPORTA URL E PORTA DI CHESHIRE CAT
CHESHIRE_CAT_URL = os.getenv("CHESHIRE_CAT_URL")
CHESHIRE_CAT_PORT = os.getenv("CHESHIRE_CAT_PORT")
#IMPOSTAZIONI LOG 
LOG_LEVEL = os.getenv("LOG_LEVEL")
formatter = ColoredFormatter(
    fmt="%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    style='%',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'white,bg_red',
    },
    reset=True
)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logging.getLogger().addHandler(ch)
logging.getLogger().setLevel(LOG_LEVEL)

#AVVIO BOT TELEGRAM
async def main():
    bot = Telegram(
        token=BOT_TOKEN, #token di accesso al bot
        cc_url=CHESHIRE_CAT_URL, 
        cc_port=CHESHIRE_CAT_PORT
    )
    await bot.run()
asyncio.run(main())
