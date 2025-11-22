from datetime import datetime

from pydantic import BaseModel


class TimeStruct(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int

    def to_datetime(self) -> datetime:
        return datetime(
            self.year, 
            self.month, 
            self.day, 
            self.hour, 
            self.minute, 
            self.second
        )
    
    def strftime(self, datetime_format: str) -> str:
        return self.to_datetime().strftime(datetime_format)


class BuddyStruct(BaseModel):
    id: int
    rarity: str
    level: int
    bangboo_rectangle_url: str


class AvatarStruct(BaseModel):
    id: int
    level: int
    element_type: int
    avatar_profession: int
    rarity: str
    rank: int
    role_square_url: str
    sub_element_type: int
