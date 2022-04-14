# import logging
import time
from sqlalchemy.sql.expression import false, null
from starlette.types import ASGIApp, Receive, Scope, Send
from routers.users.crud import ALGORITHM, SECRET_KEY
from fastapi.exceptions import HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import status, Request, WebSocket
from typing import Dict
from jose import JWTError, jwt

from database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def getAuthenticity(request: Request):
    if 'Authorization' in request.headers:
        auth = request.headers.get('Authorization')
        param, token = get_authorization_scheme_param(auth)
        try:
            jwt.decode(token, SECRET_KEY, ALGORITHM)
        except JWTError as e:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, {
                'Token': f'{e}!'})
        return token
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, {
                        'Error': 'User credential is not exist !'})


def _finditem(obj, key):
    if key in obj:
        return obj[key]
    for k, v in obj.items():
        if isinstance(v, dict):
            item = _finditem(v, key)
            if item is not None:
                return item


class Room:
    """Room state, comprising connected users."""

    def __init__(self):
        # logging.info("Creating new empty room")
        self._users: Dict[str, WebSocket] = {}
        # self._user_meta: Dict[str, UserInfo] = {}
        self.channels = {}
        self.groups = {}

    async def send(self, socket, message):
        # print('>>>>>> send to ', socket)
        await socket.send_json(message)

    async def group_add(self, group, user_id, socket):
        if self.groups.get(group):
            if self.groups[group].get(user_id):
                self.groups[group][user_id].append(socket)
            else:
                self.groups[group][user_id] = [socket]
        else:
            self.groups[group] = {}
            self.groups[group][user_id] = [socket]

    async def group_remove(self, group, user_id, socket):
        if self.groups.get(group) and self.groups[group].get(user_id) and socket in self.groups[group][user_id]:
            self.groups[group][user_id].remove(socket)
            if len(self.groups[group][user_id]) == 0:
                del self.groups[group][user_id]
            if len(self.groups[group]) == 0:
                del self.groups[group]
        else:
            raise KeyError(
                f'"{group}"/ "{user_id}" /"{ socket }" is not found')

    async def group_send(self,  message, group=None, socket_list=None):
        if group:
            if self.groups.get(group):
                for sockets in self.groups[group].values():
                    for socket in sockets:
                        await self.send(socket, message)
        elif socket_list:
            for socket in socket_list:
                await self.send(socket, message)

    async def group_active(self, group, bool=True):
        if self.groups.get(group):
            if bool:
                return len(self.groups[group]) > 1
            return len(self.groups[group])

    async def user_active(self, user_id, bool=True):
        # for value in self.groups.values():
        #     # if user_id in value:
        #     #     return True
        #     for user in value:
        #         if user == user_id:
        #             validity = True
        #             break
        # return validity
        if bool:
            if _finditem(self.groups, user_id):
                return True
            return False
        return _finditem(self.groups, user_id)


'''
    async def group_add(self, group, socket):
        """
        Adds the channel name to a group.
        """
        # Add to group dict
        if self.groups.get(group):
            self.groups[group].append(socket)
        else:
            self.groups[group] = []
            self.groups[group].append(socket)
        print(' >>> group member', self.groups)

    async def group_send(self, group, message):

        # Send to each channel
        for socket in self.groups.get(group):
            await self.send(socket, message)

    async def group_romeve(self, group, socket):
        if group in self.groups:
            if socket in self.groups[group]:
                self.groups[group].remove(socket)
            if not self.groups[group]:
                del self.groups[group]
        print(' after remove ', self.groups)

    async def group_conneted(self, group):
        if self.groups.get(group):
            return len(self.groups[group]) > 1

    async def group_exist(self, group):
        if self.groups.get(group):
            return len(self.groups[group]) > 0
'''


class RoomEventMiddleware:
    """Middleware for providing a global :class:`~.Room` instance to both HTTP
    and WebSocket scopes.

    Although it might seem odd to load the broadcast interface like this (as
    opposed to, e.g. providing a global) this both mimics the pattern
    established by starlette's existing DatabaseMiddlware, and describes a
    pattern for installing an arbitrary broadcast backend (Redis PUB-SUB,
    Postgres LISTEN/NOTIFY, etc) and providing it at the level of an individual
    request.
    """

    def __init__(self, app: ASGIApp):
        self._app = app
        self._room = Room()

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] in ("websocket"):
            scope["channel"] = self._room
        await self._app(scope, receive, send)


sample = {
    'group1': {
        'user_1': ['ws1', 'ws2'],
        'user_2': ['ws1', 'ws2', 'ws3'],
        'user_3': ['ws1', 'ws2', 'ws3']
    },
    'group2': {
        'user_1': ['ws3'],
        'user_4': ['ws1', 'ws2']
    },
    'group2': {
        'user_1': ['ws1', 'ws2', 'ws3'],
    },
}


'''
def group_remove(group,user_id,socket):
    if groups.get(group):
        if groups[group].get(user_id):
            groups[group][user_id].remove(socket)
            if len(groups[group][user_id]) ==0:
                del groups[group][user_id]
            if len(groups[group]) ==0:
                del groups[group]
                
'''
