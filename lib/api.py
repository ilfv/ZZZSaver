import asyncio
import json
from typing import TYPE_CHECKING

from aiohttp import ClientSession, ClientResponse
from cacheout import Cache

from lib.lcache import LocalCache
from lib.data_classes import (DeadlyAssaultStruct, 
                              DAChallengeResultStruct, 
                              ChallengeGIStruct, 
                              GDeadlyAssaultImgsStruct, 
                              ShiyuDefenseStruct,
                              SDImagesStruct)
from lib.save_data import SavedData
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
        self.info_cache = Cache(maxsize=512, ttl=_config.api.responce_cache_ttl)
        self.image_cache = LocalCache()
        self.session: ClientSession = None

    @staticmethod
    def _validate_headers(data: 'Any') -> bool:
        if not isinstance(data, dict):
            return False
        
        for value in data.values():
            if not isinstance(value, str):
                return False
            
        return True
    
    @property
    def _get_headers(self) -> dict[str, str]:
        return self.base_headers | _config.headers
    
    def _build_url(self, method: str, **params) -> str:
        cfg = _config.api
        return f"{cfg.protocol}://{cfg.host}{cfg.zzz_api_urls.base}{method}{'?' * (not not params)}" \
              + '&'.join(f"{key}={val}" for key, val in params.items())
    
    async def _update_session(self) -> ClientSession:
        if self.session is None or self.session.closed:
            self.session = ClientSession()
        
        return self.session

    async def _get_images(self, url: str, keys: list[str]) -> None:
        tdata = self._giret
        for key in keys[:-1]:
            tdata = tdata.setdefault(key, {})
        tdata[keys[-1]] = await self.get_img(url)
    
    async def _get_imgs(self, odata: dict, keys: list[str | int], url: str) -> None:
        tdata = odata
        for key in keys[:-1]:
            tdata = tdata.setdefault(key, {})

        tdata[keys[-1]] = await self.get_img(url)
    
    async def get_img(self, url: str, need_caching: bool = True) -> bytes:
        if url in self.image_cache:
            return self.image_cache.get(url)
        async with (await self._update_session()).get(url) as responce:
            data = await responce.content.read()
        
        if need_caching:
            self.image_cache.set(url, data)
        
        return data
    
    async def responce_handler(self, responce: ClientResponse, update_cookies: bool) -> dict:
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
        
        if update_cookies:
            cookie = _config.headers["Cookie"]
            cookie.update(responce)

        return data["data"]
    
    async def deadlyassault_info(self, 
                                 uid: int = _config.player.uid, 
                                 region: str = _config.player.region, 
                                 season: SeasonTypeEnum = SeasonTypeEnum.CURRENT,
                                 need_caching: bool = True,
                                 update_cookies: bool = True,
                                 **extra_headers) -> DeadlyAssaultStruct:
        url = self._build_url(_config.api.zzz_api_urls.deadly_assault, 
                              uid=uid, region=region, 
                              schedule_type=season.value if isinstance(season, SeasonTypeEnum) else int(season))

        if url in self.info_cache:
            return self.info_cache.get(url)
        
        headers = self._get_headers
        headers |= extra_headers if self._validate_headers(extra_headers) else {}
        
        async with (await self._update_session()).get(url, headers=headers) as responce:
            data = await self.responce_handler(responce, update_cookies)
        
        data = DeadlyAssaultStruct.model_validate(data)
        if need_caching:
            self.info_cache.set(url, data)
        
        return data
    
    async def da_challenge_res_images(self, data: DAChallengeResultStruct) -> ChallengeGIStruct:
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
            for ituple in idata:
                groug.create_task(self._get_images(*ituple))
        
        if self.session and not self.session.closed:
            await self.session.close()
        
        odata = {
            "avatars": [self._giret["avatars"][avatar_id] for avatar_id in order[0]],
            "boss": [{key: self._giret["boss"][ind][key] for key in ["icon", "race_icon", "bg_icon"]} for ind in order[1]],
            "buff": [self._giret["buff"][ind] for ind in order[2]],
            "buddy": self._giret["buddy"]
        }
        del self._giret

        return ChallengeGIStruct.model_validate(odata)
    
    async def deadlyassault_imgs(self, data: DeadlyAssaultStruct) -> GDeadlyAssaultImgsStruct | None:
        if not data.has_data:
            return None
        odata = {"challenges": [], "avatar_icon": await self.get_img(data.avatar_icon)}
        for challenge in data.list:
            odata["challenges"].append(await self.da_challenge_res_images(challenge))
        return GDeadlyAssaultImgsStruct.model_validate(odata)
    
    async def shiyu_defense_info(self, uid: int = _config.player.uid, 
                                 region: str = _config.player.region,
                                 season: SeasonTypeEnum = SeasonTypeEnum.CURRENT,
                                 need_cashing: bool = True,
                                 update_cookies: bool = True,
                                 **extra_headers):
        url = self._build_url(_config.api.zzz_api_urls.shiyu_defense, role_id=uid, server=region, need_all='true', 
                              schedule_type=season.value if isinstance(season, SeasonTypeEnum) else int(season))
        
        if url in self.info_cache:
            return self.info_cache.get(url)
        
        headers = self._get_headers
        headers |= extra_headers if self._validate_headers(extra_headers) else {}

        async with (await self._update_session()).get(url, headers=headers) as responce:
            data = await self.responce_handler(responce, update_cookies)
        
        model = ShiyuDefenseStruct.model_validate(data)

        if need_cashing:
            self.info_cache.set(url, model)
        
        return model
    
    async def shiyu_defense_imgs(self, idata: ShiyuDefenseStruct) -> SDImagesStruct:
        odata = {"schedule_id": idata.schedule_id, "avatars": {}, "monsters": {}, "buddys": {}}
        uniques = {"avatars": [], "monsters": [], "buddys": []}
        tasks = []
        
        for floor in idata.all_floor_detail:
            for node in (floor.node_1, floor.node_2):
                for avatar in node.avatars:
                    if avatar.id not in uniques["avatars"]:
                        uniques["avatars"].append(avatar.id)
                        tasks.append(asyncio.create_task(self._get_imgs(odata, ["avatars", avatar.id], avatar.role_square_url)))

                for monster in node.monster_info.list:
                    if monster.id not in uniques["monsters"]:
                        uniques["monsters"].append(monster.id)
                        for fname in ["icon_url", 'race_icon', 'bg_icon']:
                            args = (odata, ["monsters", monster.id, fname], getattr(monster, fname))
                            tasks.append(asyncio.create_task(self._get_imgs(*args)))

                buddy = node.buddy
                if buddy.id not in uniques["buddys"]:
                    uniques["buddys"].append(buddy.id)
                    tasks.append(asyncio.create_task(self._get_imgs(odata, ["buddys", buddy.id], buddy.bangboo_rectangle_url)))

        await asyncio.gather(*tasks)

        return SDImagesStruct.model_validate(odata)
    
    async def update_saved_data(self) -> None:
        _log.info("Updating saved info")
        sd = SavedData()
        msg = " data for `{key}` with id = {data_id}"
        for key, method in zip(sd.dkeys, (self.deadlyassault_info, self.shiyu_defense_info), strict=True):
            _log.info(f"Updating `{key}`")
            collection = sd.get(key)

            for i in range(1, 3):
                data = await method(season=i)
                data_id = collection.get_id(data)

                if data not in collection:
                    collection.append(data)
                    _log.info("Saved" + msg.format(key=key, data_id=data_id))
                elif data != collection.get_by_id(data_id):
                    collection[collection.find(data)] = data
                    _log.info("Updated" + msg.format(key=key, data_id=data_id))

            collection.sort()
            _log.info("Succes")
        
        if not self.session.closed:
            await self.session.close()
