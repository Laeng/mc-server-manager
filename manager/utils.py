import logging
import os
from datetime import datetime
import mcrcon
from typing import Optional

class LoggerSetup:
    @staticmethod
    def setup(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        os.makedirs('logs', exist_ok=True)
        
        handlers = [
            logging.StreamHandler(),
            logging.FileHandler(
                f'logs/{name}_{datetime.now():%Y%m%d}.log',
                encoding='utf-8'
            )
        ]
        
        for handler in handlers:
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

class RconManager:
    _instance = None
    
    def __init__(self, host, password, port):
        if not RconManager._instance:
            self.host = host
            self.password = password
            self.port = port
            self.rcon = None
            self.connected = False
            self.logger = LoggerSetup.setup('rcon')
            RconManager._instance = self
            
    @classmethod
    def get_instance(cls, host=None, password=None, port=None):
        if not cls._instance:
            if not all([host, password, port]):
                raise ValueError("RCON connection parameters required")
            return cls(host, password, port)
        return cls._instance
        
    def _connect(self):
        try:
            self.rcon = mcrcon.MCRcon(self.host, self.password, self.port)
            self.rcon.connect()
            self.connected = True
            self.logger.info("RCON connection established")
        except Exception as e:
            self.logger.error(f"RCON connection failed: {e}")
            self.rcon = None
            self.connected = False
                
    def send_command(self, command: str) -> Optional[str]:
        if not self.connected:
            self._connect()
            
        try:
            if self.connected and self.rcon:
                return self.rcon.command(command)
        except Exception as e:
            self.logger.error(f"RCON command failed: {e}")
            self.connected = False
            self.rcon = None
        return None
