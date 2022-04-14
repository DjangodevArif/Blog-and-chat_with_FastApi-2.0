from sqlalchemy.sql.expression import false
from starlette.responses import JSONResponse
from starlette.types import Message, Receive, Scope, Send
from starlette.websockets import WebSocketDisconnect
from routers.chat.models import PrivateChatRoom, RoomUnseenMessage
from routers.users.models import User
from dependencies import Room
import json
from routers.chat.schemas import RoomChatMessageRes, PrivateChatRoomRes, RoomChatMessageCreate
from routers.users.schemas import UserRes
from typing import Any, Dict, List, Optional
from routers.chat.uttils import createChatRoom, getRoombyUser, roomActiveorDeactive, getFriends, createChat, getChatMessage, messageCount, createUnseen
from routers.users.crud import getUserbyToken, get_user_by_data
from dependencies import getAuthenticity, get_db
from database import SessionLocal
from fastapi import APIRouter, HTTPException, status, Response, WebSocket
from starlette.endpoints import WebSocketEndpoint
from fastapi.param_functions import Body, Depends, Form, Query
from sqlalchemy.orm.session import Session
from fastapi.encoders import jsonable_encoder

router = APIRouter(tags=["Chat"])


@router.get("/add/{user_id}")
async def addOrRemoveFriend(user_id: int, token: str = Depends(getAuthenticity), db: Session = Depends(get_db)):
    current_user = getUserbyToken(db, token)
    other_user = get_user_by_data(db, id=user_id)
    exist = getRoombyUser(db, user_1=current_user.id, user_2=user_id)
    if exist:
        activeOrDeactive = roomActiveorDeactive(
            db, user_1=current_user.id, user_2=user_id)
        message = f"Friendship with {other_user.username} is deactivate !"
        if activeOrDeactive.is_active == True:
            message = f"Friendship with {other_user.username} is activate !"
        return JSONResponse(content={'Message': message}, status_code=status.HTTP_202_ACCEPTED)
    room = createChatRoom(db, user1=current_user.id, user2=user_id)
    return JSONResponse(content={'Message': f'"{other_user.username}" is added in your friend list !', }, status_code=status.HTTP_201_CREATED)


@router.get("/friend-list", response_model=List[UserRes])
async def getFriendList(db: Session = Depends(get_db), token: str = Depends(getAuthenticity)):
    user = getUserbyToken(db, token)
    friends = getFriends(db, user)
    return friends


@router.post("/chating/{user_id}")
async def realChat(user_id: int, content: RoomChatMessageCreate, db: Session = Depends(get_db), token: str = Depends(getAuthenticity)):
    currentuser = getUserbyToken(db, token)
    room = getRoombyUser(db, user_1=currentuser.id, user_2=user_id)
    if room:
        chat = createChat(db, room.id, content.content, currentuser)
        return chat
    return Response(content=str({"Query": " User with this query is not exist "}), status_code=status.HTTP_404_NOT_FOUND)


@router.get("/chating/{user_id}")
async def getAllChat(user_id: int, db: Session = Depends(get_db), token: str = Depends(getAuthenticity)):
    currentuser = getUserbyToken(db, token)
    room = getRoombyUser(db, user_1=currentuser.id, user_2=user_id)
    if room:
        messages = getChatMessage(db, room.id)
        return messages
    return Response(content=str({"Query": " User with this query is not exist "}), status_code=status.HTTP_404_NOT_FOUND)


@router.get("/chat-notification")
async def getUnseenMessageCount(db: Session = Depends(get_db), token: str = Depends(getAuthenticity)):
    currentuser = getUserbyToken(db, token)
    unseen_message = db.query(RoomUnseenMessage).filter(
        RoomUnseenMessage.user == currentuser.id).count()
    return JSONResponse(content={'user': currentuser.username, 'unseen_message': unseen_message}, status_code=status.HTTP_200_OK)

'''
@router.websocket("/chating/{user_id}")
async def websocket_endpoint(user_id: int, websocket: WebSocket, db: Session = Depends(get_db)):
    #  db: Session = Depends(get_db)
    channel: Optional[Room] = websocket.scope.get("channel")
    currentuser: Optional[User] = None
    room: Optional[PrivateChatRoom] = None
    room_name: Optional[str] = None
    # websocket : connect
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            print('data', data)
            if 'token' in data:
                currentuser = getUserbyToken(db, data['token'])
                room = getRoombyUser(db, user_1=currentuser.id, user_2=user_id)
                room_name = f"room_{room.id}"
                if room:
                    await channel.group_add(room_name, websocket)
                    messages = getChatMessage(db, room.id)
                    loaded = jsonable_encoder(messages)
                    # await websocket.send_json({'fetch_data': loaded, 'current_user': jsonable_encoder(currentuser)})
                    await channel.group_send(room_name, {'fetch_data': loaded, 'current_user': jsonable_encoder(currentuser)})
            elif 'new_message' in data:
                chat = createChat(
                    db, room.id, data['new_message'], currentuser)
                # await websocket.send_json({'accept_message': jsonable_encoder(chat)})
                await channel.group_send(room_name, {'accept_message': jsonable_encoder(chat)})
    except WebSocketDisconnect:
        await channel.group_romeve(room_name, websocket)

'''


@router.websocket_route("/chating/{user_id}")
class Chatroom(WebSocketEndpoint):

    encoding = "text"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel: Optional[Room] = None
        self.currentuser: Optional[User] = None
        self.room: Optional[PrivateChatRoom] = None
        self.room_name: Optional[str] = None
        self.user_key: Optional[str] = None
        self.user_id: int = None

    async def on_connect(self, websocket: WebSocket):
        self.channel = self.scope.get('channel')
        self.user_id = self.scope.get('path_params')['user_id']
        await websocket.accept()

    async def on_receive(self, websocket: WebSocket, data: Dict) -> None:
        payload = json.loads(data)
        db = SessionLocal()
        if 'token' in payload:
            self.currentuser = getUserbyToken(db, payload['token'])
            self.room = getRoombyUser(
                db, user_1=self.currentuser.id, user_2=self.user_id)

            self.room_name = f"room_{self.room.id}"
            self.user_key = f"user_{self.currentuser.id}"

            if self.room:
                await self.channel.group_add(self.room_name, self.user_key, websocket)

                messages = getChatMessage(db, self.room.id)
                message_count = messageCount(db, self.room.id)

                connected = await self.channel.group_active(self.room_name)

                if connected:
                    await self.channel.group_send(group=self.room_name, message={'connected': True})

                await self.channel.send(websocket, {'fetch_data': jsonable_encoder(messages), 'total_message': message_count, 'current_user': jsonable_encoder(self.currentuser)})
                # await self.channel.group_send(group=self.room_name,message= {'fetch_data': loaded, 'current_user': jsonable_encoder(self.currentuser)})

        elif 'new_message' in payload:
            chat = createChat(
                db, self.room.id, payload['new_message'], self.currentuser)
            await self.channel.group_send(group=self.room_name, message={'accept_message': jsonable_encoder(chat)})
            if await self.channel.user_active(f"user_{self.user_id}"):
                if not await self.channel.group_active(self.room_name):
                    user_socket = await self.channel.user_active(f"user_{self.user_id}", bool=False)
                    await self.channel.group_send(socket_list=user_socket, message={"new_unseen_message": True, 'user': self.currentuser.id, 'message': jsonable_encoder(chat.content)})
            else:
                unseen_message = createUnseen(
                    db, user_id=self.user_id, message_id=chat.id)
        elif 'load_message' in payload:
            messages = getChatMessage(
                db, self.room.id, offset=payload['load_message'])
            await self.channel.send(websocket, {'load_message': jsonable_encoder(messages)})
        db.close()

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self.channel.group_remove(self.room_name, self.user_key, websocket)

        # it's only applicable for private room (e.g. means only 2 user room).
        member_exist = await self.channel.group_active(self.room_name)
        if not member_exist:
            await self.channel.group_send(group=self.room_name, message={'connected': False})
