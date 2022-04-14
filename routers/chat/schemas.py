from datetime import datetime, date
from ..users.schemas import UserRes
from typing import Any, List, Optional
from pydantic import BaseModel


class PrivateChatRoomCreate(BaseModel):
    user1: int
    user2: int


class PrivateChatRoomRes(PrivateChatRoomCreate):
    id: int
    is_active: bool
    # messages: 'RoomChatMessageRes'

    class Config:
        orm_mode = True


class RoomChatMessageCreate(BaseModel):

    content: str


class RoomChatMessageRes(RoomChatMessageCreate):
    id: int
    user: int
    room_id: int
    timestamp: date
    foo: str
    room: PrivateChatRoomRes

    class Config:
        orm_mode = True
