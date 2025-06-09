import asyncio
import json
from functools import cached_property
from typing import TYPE_CHECKING

from aiohttp import ClientSession, ClientResponse
from cacheout import Cache

from lib.data_classes import DeadlyAssaultStruct, ChallengeResultStruct, GetImagesReturnStruct
from lib.enums import SeasonTypeEnum
from lib.errors import ApiError, EmptyResponce
from lib.settings import Config
from lib.logger import get_logger
from lib.utils import singleton

if TYPE_CHECKING:
    from typing import Any

_log = get_logger(__file__, "ApiLog")
_config = Config().get()


@singleton
class Api:
    def __init__(self):
        self.base_headers = {
            "Origin": "https://act.hoyolab.com", 
            "Referer": "https://act.hoyolab.com/", 
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"
        }
        self.mem_detail_cache = Cache(maxsize=512, ttl=_config.api.mem_detail_cache_ttl)
        self.image_cache = Cache(maxsize=512, ttl=_config.api.image_cache_ttl)
        self.session: ClientSession = None

    @staticmethod
    def _validate_headers(data: 'Any') -> bool:
        if not isinstance(data, dict):
            return False
        
        for value in data.values():
            if not isinstance(value, str):
                return False
            
        return True
    
    @cached_property
    def _get_headers(self) -> dict[str, str]:        
        return self.base_headers | _config.headers
    
    def _build_url(self, **params) -> str:
        cfg = _config.api
        return f"{cfg.protocol}://{cfg.host}{cfg.zzz_api_urls.base}{cfg.zzz_api_urls.mem_detail}{'?' * (not not params)}" \
              + '&'.join(f"{key}={val}" for key, val in params.items())
    
    async def _update_session(self) -> ClientSession:
        if self.session is None or self.session.closed:
            self.session = ClientSession()
        
        return self.session
    
    async def get_img(self, url: str, need_caching: bool = True) -> bytes:
        if url in self.image_cache:
            return self.image_cache.get(url)
        async with (await self._update_session()).get(url) as responce:
            data = await responce.content.read()
        
        if need_caching:
            self.image_cache.set(url, data)
        
        return data

    async def _get_images(self, url: str, keys: list[str]) -> None:
        tdata = self._giret
        for key in keys[:-1]:
            tdata = tdata.setdefault(key, {})
        tdata[keys[-1]] = await self.get_img(url)
    
    async def responce_handler(self, responce: ClientResponse) -> dict:
        responce_text = await responce.text()
        data = json.loads(responce_text)
        error_cls = message = None

        if responce.status != 200:
            message = f"Bad request, status code - {responce.status}"
            error_cls = ApiError
        elif not data:
            message = "HoyoverseApi return empty responce"
            error_cls = EmptyResponce
        elif data["retcode"] != 0:
            message = f"HoyoverseApi says: {data['message']}"
            error_cls = ApiError
        
        if error_cls or message:
            _log.error(f"{error_cls.__name__}: {message}")
            raise error_cls(message)

        return data["data"]
    
    async def get_deadlyassault_info(self, 
                                     uid: int = _config.player.uid, 
                                     region: str = _config.player.region, 
                                     season: SeasonTypeEnum = SeasonTypeEnum.CURRENT,
                                     need_caching: bool = True,
                                     **extra_headers) -> DeadlyAssaultStruct:
        url = self._build_url(uid=uid, region=region, schedule_type=season.value if isinstance(season, SeasonTypeEnum) else int(season))

        if url in self.mem_detail_cache:
            return self.mem_detail_cache.get(url)
        
        headers = self._get_headers
        headers |= extra_headers if self._validate_headers(extra_headers) else {}
        
        async with (await self._update_session()).get(url, headers=headers) as responce:
            data = await self.responce_handler(responce)
        
        data = DeadlyAssaultStruct.model_validate(data)
        if need_caching:
            self.mem_detail_cache.set(url, data)
        
        return data
    
    
    async def get_cres_images(self, data: ChallengeResultStruct) -> GetImagesReturnStruct:
        order = [[avatar.id for avatar in data.avatar_list], 
                 [*range(len(data.boss))], 
                 [*range(len(data.buffer))]]
        self._giret = {"avatars": {}, "boss": {}, "buff": {}, "buddy": ...}

        idata = [(avatar.role_square_url, ["avatars", avatar.id]) for avatar in data.avatar_list]
        idata.extend((getattr(boss, key), ["boss", ind, key]) for ind, boss in enumerate(data.boss) \
                        for key in ["icon", "race_icon", "bg_icon"])
        idata.extend((buff.icon, ["buff", ind]) for ind, buff in enumerate(data.buffer))
        idata.append((data.buddy.bangboo_rectangle_url, ["buddy"]))

        async with asyncio.TaskGroup() as groug:
            for itup in idata:
                groug.create_task(self._get_images(*itup))
        
        await self.session.close()
        
        odata = {
            "avatars": [self._giret["avatars"][avatar_id] for avatar_id in order[0]],
            "boss": [{key: self._giret["boss"][ind][key] for key in ["icon", "race_icon", "bg_icon"]} for ind in order[1]],
            "buff": [self._giret["buff"][ind] for ind in order[2]],
            "buddy": self._giret["buddy"]
        }
        del self._giret

        return GetImagesReturnStruct.model_validate(odata)
