import asyncio
import logging 
import json

from cheshire_cat_api import CatClient, Config

class Connection:
    
    def __init__(self,id,out_queue,cc_url,cc_port):
        self.id = id
        self._loop = asyncio.get_running_loop()
        self._out_queue : asyncio.Queue = out_queue
        conf = Config(cc_url,cc_port,id)
        self.cat_client = CatClient(
            config=conf,
            on_open=self._on_open,
            on_close=self._on_close,
            on_message=self._ccat_message_callback
        )
        self.send = self.cat_client.send
        self._stop_waiting_connection = None
    
    async def connect(self):
        if self._stop_waiting_connection is not None:
            logging.warning(f"")
            return
        self.cat_client.connect_ws()
        self._stop_waiting_connection = asyncio.Event()
        await self._stop_waiting_connection.wait()
        self._stop_waiting_connection = None
    
    def on_open(self):
        if self._stop_waiting_connection:
            self._stop_waiting_connection.set()
    
    def on_close(self):
        if self._stop_waiting_connection:
            self._stop_waiting_connection.set()
    
    def _cat_message_cb(self,message):
        mex = json.loads(message)
        self._loop.call_soon_threadsafe(self._out_queue.put_nowait,(mex,self.id))

    @property
    def is_connected(self):
        return self.cat_client.is_ws_connected