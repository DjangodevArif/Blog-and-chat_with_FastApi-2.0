from datetime import datetime, date
from xml.etree.ElementInclude import include

from pydantic.types import Json


from typing import Any, ForwardRef, List, Optional, Union
from pydantic import BaseModel, Field
from sqlalchemy.sql.expression import null

from routers.users.schemas import UserRes

# Reply model


class CreateReply(BaseModel):
    comment_id: int
    content: str


class ResReply(CreateReply):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

# Comment model


class CreateComment(BaseModel):
    content: str


class ResComment(CreateComment):
    id: int
    user_id: int
    feed_id: int
    timestamp: datetime
    replys: List[ResReply] = []

    class Config:    # make sure C of "Config" is upperCase
        orm_mode = True


# Reaction model

# ResFeed = ForwardRef('ResFeed')
class ResFeedForReaction(BaseModel):
    title: Optional[str]
    content: str
    media: Union[dict, list, set, str, None] = {}
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class CreateReaction(BaseModel):
    react: Any


class ResReaction(CreateReaction):
    id: int
    user_id: int
    feed_id: int
    user: UserRes
    feed: ResFeedForReaction

    class Config:
        orm_mode = True

# ResReaction.update_forward_refs()


#  Feed model
class ResReactionForFeed(BaseModel):
    id: int
    user: UserRes
    # user:UserRes =Field(..., exclude={'username'})  # it's not working
    react: Any

    class Config:
        orm_mode = True
        # fields ={'user':{'exclude':{'id','email'}}}  # it's not working


class CreateFeed(BaseModel):
    title: Optional[str]
    content: str
    # remove str,None from media its just for temporary
    media: Union[dict, list, set, str, None] = {}   # as a Json


class ResFeed(CreateFeed):
    id: int
    user: UserRes
    timestamp: datetime
    comments: List[ResComment] = []
    reacts: List[ResReactionForFeed] = []

    class Config:
        orm_mode = True
