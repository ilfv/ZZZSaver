import os
import json
from typing import TYPE_CHECKING

from .data_classes import DeadlyAssaultStruct
from .logger import get_logger
from .utils import singleton

if TYPE_CHECKING:
    from typing import Any, Callable

_log = get_logger(__file__, "SavedDataApi")


@singleton
class SavedData:
    data: list[DeadlyAssaultStruct]

    def __init__(self, path: str = "data.json"):
        self.data = []
        if os.path.exists(path):
            tdata: dict = json.load(open(path, encoding="utf-8"))
            
            for model in tdata.get("data", []):
                self.data.append(DeadlyAssaultStruct.model_validate(model))
    
    def __getitem__(self, index):
        return self.data[index]
    
    def __delitem__(self, index):
        del self.data[index]
    
    def __len__(self):
        return len(self.data)
    
    def load_extra_save(self, path: str = "extra.txt", try_save2json: bool = True):
        for line in open(path, encoding="utf-8").readlines():
            self.data.append(DeadlyAssaultStruct.model_validate_json(line.strip()))

        if try_save2json:
            self.save2json()
    
    def get(self) -> list[DeadlyAssaultStruct]:
        return self.data
    
    def sort(self, 
             key: 'Callable[[DeadlyAssaultStruct], Any]' = lambda x: x.start_time.to_datetime(), 
             reverse: bool = True) -> 'SavedData':
        self.data.sort(key=key, reverse=reverse)
        return self
    
    def append(self, struct: DeadlyAssaultStruct) -> 'SavedData':
        self.data.append(struct)
        return self
    
    def save2json(self, path: str = "data.json") -> bool:
        try:
            json.dump({"data": [model.model_dump() for model in self.data]}, open(path, 'w', encoding='utf-8'), indent=2)
            result = True
        except Exception as exc:
            _log.error(f"Error '{exc}' while saving data")
            text = '\n'.join(model.model_dump_json() for model in self.data)
            open("extra.txt", 'w', encoding='utf-8').write(text)
            result = False
        
        return result
