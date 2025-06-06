from datetime import datetime

from pydantic import BaseModel


class TimeStruct(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int

    def to_datetime(self):
        return datetime(
            self.year, 
            self.month, 
            self.day, 
            self.hour, 
            self.minute, 
            self.second
        )
    

class BossStruct(BaseModel):
    icon: str
    name: str
    race_icon: str
    bg_icon: str


class BufferStruct(BaseModel):
    icon: str
    desc: str
    name: str


class AvatarStruct(BaseModel):
    id: int
    level: int
    element_type: int
    avatar_profession: int
    rarity: str
    rank: int
    role_square_url: str
    sub_element_type: int


class BuddyStruct(BaseModel):
    id: int
    rarity: str
    level: int
    bangboo_rectangle_url: str
    

class RResultStruct(BaseModel):
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

    nick_name: str
    avatar_icon: str
    total_score: int
    total_star: int
    zone_id: int
    rank_percent: int

    list: list[RResultStruct]


class GIBossStruct(BaseModel):
    icon: bytes
    race_icon: bytes
    bg_icon: bytes


class GetImagesReturnStruct(BaseModel):
    avatars: list[bytes]
    boss: list[GIBossStruct]
    buff: list[bytes]
    buddy: bytes
