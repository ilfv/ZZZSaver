from pydantic import BaseModel, Field

from PIL import Image

from .base import TimeStruct, AvatarStruct, BuddyStruct


class SDRatingStruct(BaseModel):
    times: int
    rating: str


class SDBuffStruct(BaseModel):
    title: str
    text: str


class SDMonsterStruct(BaseModel):
    id: int
    name: str
    weak_element_type: int
    ice_weakness: int
    fire_weakness: int
    elec_weakness: int
    ether_weakness: int
    physics_weakness: int
    icon_url: str
    race_icon: str
    bg_icon: str


class SDMonsterInfoStruct(BaseModel):
    level: int
    list: list[SDMonsterStruct]


class SDFloorNodeStruct(BaseModel):
    avatars: list[AvatarStruct]
    buddy: BuddyStruct
    element_type_list: list[int]
    monster_info: SDMonsterInfoStruct
    battle_time: int


class SDFloorDetailStruct(BaseModel):
    layer_index: int
    rating: str
    layer_id: int

    buffs: list[SDBuffStruct]
    node_1: SDFloorNodeStruct
    node_2: SDFloorNodeStruct
    challenge_time: str
    zone_name: str
    floor_challenge_time: TimeStruct


class ShiyuDefenseStruct(BaseModel):
    schedule_id: int
    begin_time: str
    end_time: str
    hadal_begin_time: TimeStruct
    hadal_end_time: TimeStruct
    fast_layer_time: int
    max_layer: int
    battle_time_47: int
    has_data: bool

    rating_list: list[SDRatingStruct]
    all_floor_detail: list[SDFloorDetailStruct]

    def __eq__(self, value):
        return isinstance(value, self.__class__) and self.schedule_id == value.schedule_id
    

class SDImgMonsterStruct(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    icon: bytes | Image.Image = Field(..., alias="icon_url")
    race_icon: bytes | Image.Image
    bg_icon: bytes | Image.Image


class SDImagesStruct(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    schedule_id: int

    avatars: dict[int, bytes | Image.Image]
    monsters: dict[int, SDImgMonsterStruct]
    buddys: dict[int, bytes | Image.Image]
