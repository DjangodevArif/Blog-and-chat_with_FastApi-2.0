
from typing import List
from fastapi.param_functions import Depends
from sqlalchemy.sql.elements import or_
from routers.chat.schemas import PrivateChatRoomRes
from routers.chat.models import PrivateChatRoom, RoomChatMessage, RoomUnseenMessage
from routers.users.models import User
from sqlalchemy.orm.session import Session


def createChatRoom(db: Session, user1: int, user2: int):
    db_Room = PrivateChatRoom(user1=user1, user2=user2)
    db.add(db_Room)
    db.commit()
    db.refresh(db_Room)
    return db_Room


def getRoombyUser(db: Session, user_1: int, user_2: int):
    # may_1 = db.query(PrivateChatRoom).get({"user1": user_1, "user2": user_2})
    may_1 = db.query(PrivateChatRoom).filter(
        PrivateChatRoom.user1 == user_1, PrivateChatRoom.user2 == user_2).first()
    if may_1:
        return may_1
    return db.query(PrivateChatRoom).filter(PrivateChatRoom.user1 == user_2, PrivateChatRoom.user2 == user_1).first()


def getRoombyId(db: Session, id: int):
    return db.query(PrivateChatRoom).get(id)


def roomActiveorDeactive(db: Session, user_1: int, user_2: int):
    room = getRoombyUser(db, user_1, user_2)
    room.is_active = not room.is_active
    db.commit()
    return room


def getUserRooms(db: Session, user: User):
    rooms = db.query(PrivateChatRoom).filter(
        or_(PrivateChatRoom.user1 == user.id, PrivateChatRoom.user2 == user.id), PrivateChatRoom.is_active == True).all()
    return rooms


def getFriends(db: Session, user: User):
    rooms = getUserRooms(db, user)
    friendlist = []
    for i in rooms:
        if i.user1 == user.id:
            friendlist.append(i.user2)
        else:
            friendlist.append(i.user1)
    friends = db.query(User).filter(User.id.in_(friendlist)).all()
    return friends


def createChat(db: Session, room_id: int, content: str, user: User):
    chat = RoomChatMessage(user=user.id, room_id=room_id, content=content)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def getChatMessage(db: Session, room_id: int, user: User = None, offset: int = 0, limit: int = 10):
    # roomchat = db.query(RoomChatMessage).get({'room_id': room_id})
    # roomchat = db.query(RoomChatMessage).filter(
    #     RoomChatMessage.room_id == room_id).order_by(RoomChatMessage.timestamp).offset(0).limit(10).all()
    return db.query(RoomChatMessage).filter(
        RoomChatMessage.room_id == room_id).order_by(RoomChatMessage.id.desc()).offset(offset).limit(limit).all()


def messageCount(db: Session, room_id: int):
    return db.query(RoomChatMessage).filter(
        RoomChatMessage.room_id == room_id).count()


def createUnseen(db: Session, user_id: int, message_id: int):
    unseenMessage = RoomUnseenMessage(user=user_id, message=message_id)
    db.add(unseenMessage)
    db.commit()
    db.refresh(unseenMessage)
    return unseenMessage


def getUnseenMessages():
    pass
