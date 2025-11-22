from pydantic import BaseModel

from lib.cookies import Cookie


class ZzzApiUrlsStruct(BaseModel):
    base: str
    deadly_assault: str
    shiyu_defense: str


class ApiStruct(BaseModel):
    auto_update_cookies: bool
    protocol: str
    host: str
    responce_cache_ttl: int
    image_cache_ttl: int

    zzz_api_urls: ZzzApiUrlsStruct


class PlayerStruct(BaseModel):
    uid: int
    region: str


class LocalCacheStruct(BaseModel):
    caching: bool
    cache_dir: str


class ConfigStruct(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    logs_dir: str
    headers: dict[str, str | Cookie]

    api: ApiStruct
    player: PlayerStruct

    local_cache: LocalCacheStruct
