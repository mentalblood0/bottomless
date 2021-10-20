import json
from requests import Response

class ModuleClientBase:
    _server = None
    _server_url:str = None
    
    def __init__(self, config):
        self._server = config['server']
        self._server_url = f"http://{self._server['host']}:{self._server['port']}"
        
    def _throw(desc:str):
        return
    
    def _checkResponse(self, response:Response)->Response:
        if not response.ok:
            self._throw(f"Некорректный ответ от сервера: {response.status_code}")
        
        if not response.json():
            self._throw(f"Некорректный формат ответа")
        
        return response