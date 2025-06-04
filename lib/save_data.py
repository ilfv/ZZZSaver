import os
import json

from .data_classes import DeadlyAssaultStruct
from .logger import get_logger
from .utils import singleton

_log = get_logger(__file__, "SavedDataApi")


@singleton
class SavedData:
    def __init__(self, path: str = "data.json"):
        self.data = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else []
    
    def __getitem__(self, index):
        return self.data[index]
    
    def __delitem__(self, index):
        del self.data[index]
    
    def __len__(self):
        return len(self.data)
    
    def get(self) -> list[DeadlyAssaultStruct]:
        return self.data
    
    def append(self, struct: DeadlyAssaultStruct) -> 'SavedData':
        self.data.append(struct)
        return self
    
    def save2json(self, path: str = "data.json") -> bool:
        try:
            json.dump({"data": self.data}, open(path, 'w', encoding='utf-8'), indent=2)
            result = True
        except Exception as exc:
            _log.error(f"Error '{exc}' while saving data")
            open("extra.txt", 'w', encoding='utf-8').write(str(self.data))
            result = False
        
        return result
