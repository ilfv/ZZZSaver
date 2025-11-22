from __future__ import annotations

import os
import json
from typing import TYPE_CHECKING, Literal

from .data_classes import DeadlyAssaultStruct, ShiyuDefenseStruct
from .settings import Config
from .logger import get_logger
from .utils import singleton

if TYPE_CHECKING:
    from typing import Any, Union, Callable

Tgvar =  DeadlyAssaultStruct | ShiyuDefenseStruct
Tkeys = Literal["deadly_assault", "shiyu_defense"]
_log = get_logger(__file__, "SavedDataApi")
_config = Config().get()


class Collection:
    _gattr_by_class = {DeadlyAssaultStruct: "zone_id", ShiyuDefenseStruct: "schedule_id"}
    _tattr_by_class = {DeadlyAssaultStruct: "start_time", ShiyuDefenseStruct: "hadal_begin_time"}

    def __init__(self, data: list[Tgvar]):
        self.data = data
    
    def __contains__(self, item: Tgvar) -> bool:
        return item in self.data
    
    def __getitem__(self, index: int) -> Tgvar:
        return self.data[index]
    
    def __setitem__(self, index: int, value: Tgvar) -> None:
        self.data[index] = value
    
    def __len__(self) -> int:
        return len(self.data)

    def find(self, value: Tgvar) -> int:
        for i in range(len(self.data)):
            if self.data[i] == value:
                return i
            
        return -1

    def sort(self, key: 'Callable[[Tgvar], Any]' = "gen", reverse: bool = True) -> Collection:
        if key == "gen":
            attr_name = self._tattr_by_class[self.data[0].__class__]
            key = lambda x: getattr(x, attr_name).to_datetime()
        
        self.data.sort(key=key, reverse=reverse)
        return self
    
    def get_id(self, data: Tgvar) -> int:
        attr_name = self._gattr_by_class[data.__class__]
        return getattr(data, attr_name)
    
    def get_by_id(self, iid: int) -> Tgvar:
        for model in self.data:
            if self.get_id(model) == iid:
                return model
    
    def append(self, data: Tgvar) -> Collection:
        self.data.append(data)
        return self


@singleton
class SavedData:
    data: 'dict[str, list[Union[DeadlyAssaultStruct, ShiyuDefenseStruct]]]'
    dkeys = ["deadly_assault", "shiyu_defense"]
    key2class: 'dict[str, Union[DeadlyAssaultStruct, ShiyuDefenseStruct]]' = {"deadly_assault": DeadlyAssaultStruct, 
                                                                              "shiyu_defense": ShiyuDefenseStruct}

    def __init__(self, save_dir: str = "data"):
        self.data = {}
        
        for key in self.dkeys:
            self.data[key] = []

        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        
        path = os.path.join(save_dir, f'{_config.player.uid}.json')

        if os.path.exists(path):
            tdata: dict[str, str] = json.load(open(path, encoding="utf-8"))
            
            if not tdata:
                return
            
            for key in self.dkeys:
                for val in tdata[key]:
                    cls = self.key2class[key]
                    self.data[key].append(cls.model_validate(val))
    
    def get(self, key: Tkeys) -> Collection:
        return Collection(self.data[key])
    
    def get_by_id(self, key: Tkeys, iid: int) -> DeadlyAssaultStruct | ShiyuDefenseStruct | None:
        if key == "deadly_assault":
            attr_name = "zone_id"
        elif key == "shiyu_defense":
            attr_name = "schedule_id"
        else:
            raise ValueError("invalid value for `key`")
        
        for model in self.data[key]:
            if getattr(model, attr_name) == iid:
                return model
    
    def load_extra_save(self, path: str = "extra.txt", try_save2json: bool = True):
        for line in open(path, encoding="utf-8").readlines():
            line = line.strip()
            key = line[:line.find(":")]
            line = line[line.find(":") + 2:]
            self.data[key].append(self.key2class[key].model_validate_json(line.strip()))

        if try_save2json:
            self.save2json()
    
    def save2json(self, save_dir: str = "data") -> bool:
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        
        path = os.path.join(save_dir, f"{_config.player.uid}.json")

        try:
            json.dump({mkey: [model.model_dump() for model in self.data[mkey]] for mkey in self.dkeys}, 
                      open(path, 'w', encoding='utf-8'), indent=2)
            result = True
        except Exception as exc:
            _log.error(f"Error '{exc}' while saving data")
            text = '\n'.join(f"{mkey}: " + model.model_dump_json() for mkey in self.dkeys for model in self.data[mkey])
            open("extra.txt", 'w', encoding='utf-8').write(text)
            result = False
        
        return result
    
    def clear_duplicates(self):
        for key in self.dkeys:
            temp = []
            for model in self.data[key]:
                if model not in temp:
                    temp.append(model)
            self.data[key] = temp
