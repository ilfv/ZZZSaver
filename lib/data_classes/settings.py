from pydantic import BaseModel


class ZzzApiUrlsStruct(BaseModel):
    base: str
    mem_detail: str


class ApiStruct(BaseModel):
    protocol: str
    host: str
    request_timeout: float
    cache_ttl: int

    zzz_api_urls: ZzzApiUrlsStruct


class PlayerStruct(BaseModel):
    uid: int
    region: str


class ConfigStruct(BaseModel):
    logs_dir: str
    headers: dict[str, str]

    api: ApiStruct
    player: PlayerStruct
