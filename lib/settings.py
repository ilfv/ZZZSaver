import os

from .cookies import Cookie
from .data_classes import ConfigStruct
from .env_load import load_env
from .utils import singleton

CONFIG_JSON_PATH = "config.json"

load_env()

@singleton
class Config:
    def __init__(self) -> None:
        self.cfg = ConfigStruct.model_validate_json(open(CONFIG_JSON_PATH, encoding="utf-8").read())
        self.cfg.headers["Cookie"] = Cookie(os.environ["Cookie"])
    
    def get(self) -> ConfigStruct:
        return self.cfg
