from .data_classes import ConfigStruct
from .utils import singleton

CONFIG_JSON_PATH = "config.json"

@singleton
class Config:
    def __init__(self) -> None:
        self.cfg = ConfigStruct.model_validate_json(open(CONFIG_JSON_PATH, encoding="utf-8").read())
    
    def get(self) -> ConfigStruct:
        return self.cfg
