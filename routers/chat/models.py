from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, Date, Integer, String, DateTime
from routers.users.models import User
# from ...database import Base


class PrivateChatRoom(Base):
    __tablename__ = "privatechatroom"
    id = Column(Integer, primary_key=True)
    user1 = Column(Integer, ForeignKey(User.id))
    user2 = Column(Integer, ForeignKey(User.id))
    is_active = Column(Boolean, default=True)
    messages = relationship(
        'RoomChatMessage', backref='room')

    def __repr__(self) -> str:
        return "<PrivateChatRoom beetwen (id='%s') and (id='%s')>" % (
            self.user1, self.user2)


class RoomChatMessage(Base):
    __tablename__ = "roomchatmessage"
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey(User.id))
    room_id = Column(Integer, ForeignKey('privatechatroom.id'))
    timestamp = Column(DateTime, default=datetime.now())
    content = Column(String)

    # def __str__(self) -> str:
    #     return f"<RoomChatMessage (user={self.user}) (room_id={self.room_id})>"

    def __repr__(self) -> str:
        return "<RoomChatMessage  (user='%s') and (room='%s')>" % (
            self.user, self.room_id)


class RoomUnseenMessage(Base):
    __tablename__ = "roomUnseenMessage"

    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey(User.id))
    message = Column(Integer, ForeignKey('roomchatmessage.id'))

    def __repr__(self) -> str:
        return "<RoomUnseenMessage  (user='%s') and (message='%s')>" % (
            self.user, self.message)
