from PIL import Image
from pydantic import BaseModel

from .base import TimeStruct, AvatarStruct, BuddyStruct


class BossStruct(BaseModel):
    icon: str
    name: str
    race_icon: str
    bg_icon: str


class BufferStruct(BaseModel):
    icon: str
    desc: str
    name: str
    

class DAChallengeResultStruct(BaseModel):
    score: int
    star: int
    total_star: int
    challenge_time: TimeStruct
    boss: list[BossStruct]
    buffer: list[BufferStruct]
    avatar_list: list[AvatarStruct]
    buddy: BuddyStruct


class DeadlyAssaultStruct(BaseModel):
    start_time: TimeStruct
    end_time: TimeStruct

    has_data: bool
    nick_name: str
    avatar_icon: str
    total_score: int
    total_star: int
    zone_id: int
    rank_percent: int

    list: list[DAChallengeResultStruct]

    def __eq__(self, value):
        return isinstance(value, self.__class__) and self.zone_id == value.zone_id


class GIBossStruct(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    icon: bytes | Image.Image
    race_icon: bytes | Image.Image
    bg_icon: bytes | Image.Image


class ChallengeGIStruct(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    avatars: list[bytes | Image.Image]
    boss: list[GIBossStruct]
    buff: list[bytes | Image.Image]
    buddy: bytes | Image.Image


class GDeadlyAssaultImgsStruct(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    challenges: list[ChallengeGIStruct]
    avatar_icon: bytes | Image.Image
