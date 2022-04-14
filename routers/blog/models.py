
import enum
from datetime import datetime

from pydantic import validator
from sqlalchemy.orm import relationship
from routers.users.models import User
from database import Base
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import JSON, Boolean, DateTime, Enum, Integer, String


class Feed(Base):
    __tablename__ = "feed"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User)
    title = Column(String(80), nullable=True)
    content = Column(String)
    comments = relationship("Comment", backref="feed", lazy=True)
    reacts = relationship("Reaction", backref="feed")
    timestamp = Column(DateTime, default=datetime.now())
    media = Column(JSON)  # schema will be Any or Union[dict,list,set]

    @validator('content')
    def validate_content(cls, v, values, **kwargs):
        print('>>>> cls', cls)
        print('>>>>> v', v)
        print('>>>>  values', values)
        print('>>>>>  kwargs', kwargs)
        return None

    def __repr__(self) -> str:
        return "<Feed-('%s') of (user_id='%s') is (content='%s')" % (self.id, self.user_id, self.content[0:15])


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    feed_id = Column(Integer, ForeignKey("feed.id"))
    content = Column(String(400))
    replys = relationship("Reply", backref="main_comment", lazy=True)
    timestamp = Column(DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return "<Comment-('%s') of (user_id='%s')" % (self.id, self.user_id)


class Reply(Base):
    __tablename__ = "reply"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    comment_id = Column(Integer, ForeignKey("comment.id"))
    content = Column(String(400))
    timestamp = Column(DateTime, default=datetime.now())

    def __repr__(self) -> str:
        return "<Reply-('%s') of (user_id='%s')" % (self.id, self.user_id)


class MyReaction(enum.Enum):
    like = 'like'
    love = 'love'
    rich = 'rich'
    broken = 'broken'


class Reaction(Base):
    __tablename__ = "reaction"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    feed_id = Column(Integer, ForeignKey(Feed.id))
    user = relationship(User)
    react = Column(Enum(MyReaction))

    # need more test
    # feed = relationship("Feed",back_populates="reactions") # back_populates and backref both are same

    def __repr__(self) -> str:
        return "<Reaction-('%s') is (react = '%s') of (feed_id = '%s') >" % (self.id, self.react, self.feed_id)
