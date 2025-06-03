import json
from typing import Any

from aiohttp import ClientSession, ClientResponse
from cacheout import Cache

from .data_classes import DeadlyAssaultStruct
from .enums import SeasonTypeEnum
from .errors import ApiError, EmptyResponce
from .settings import Config
from .logger import get_logger
from .utils import singleton

_log = get_logger(__file__, "ApiLog")
_config = Config().get()


@singleton
class Api:
    base_headers = {
        "Origin": "https://act.hoyolab.com", 
        "Referer": "https://act.hoyolab.com/", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:139.0) Gecko/20100101 Firefox/139.0"
    }
    cache = Cache(ttl=_config.api.cache_ttl)
    session: ClientSession = None

    @staticmethod
    def _validate_headers(data: Any) -> bool:
        if not isinstance(data, dict):
            return False
        
        for value in data.values():
            if not isinstance(value, str):
                return False
            
        return True
    
    async def _update_session(self) -> ClientSession:
        if self.session is None or self.session.closed:
            self.session = ClientSession()
        
        return self.session

    def _get_headers(self, **extra) -> dict[str, str]:
        validation_failed = False

        if extra:
            if not self._validate_headers(extra):
                _log.warning("invalid extra headers, ignoring")
                validation_failed = True
        
        return self.base_headers | _config.headers | (extra if not validation_failed else {})
    
    def _build_url(self, **params) -> str:
        cfg = _config.api
        return f"{cfg.protocol}://{cfg.host}{cfg.zzz_api_urls.base}{cfg.zzz_api_urls.mem_detail}?" + '&'.join(f"{key}={val}" for key, val in params.items())
    
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
                                     **extra_headers) -> DeadlyAssaultStruct:
        url = self._build_url(uid=uid, region=region, schedule_type=season.value if isinstance(season, SeasonTypeEnum) else int(season))
        headers = self._get_headers(**extra_headers)
        
        async with (await self._update_session()).get(url, headers=headers) as responce:
            data = await self.responce_handler(responce)
        
        return DeadlyAssaultStruct.model_validate(data)
