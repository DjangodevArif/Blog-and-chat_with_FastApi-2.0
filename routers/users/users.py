from typing import List

from fastapi.param_functions import Body, Depends, Header
from . import crud, schemas
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm.session import Session
from dependencies import get_db, getAuthenticity

router = APIRouter(tags=["User"])


@router.get("/users", response_model=List[schemas.UserRes])
async def allUsers(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    return crud.get_users(db, skip, limit)


@router.get("/me", response_model=schemas.UserRes)
async def getMe(token: str = Depends(getAuthenticity), db: Session = Depends(get_db)):
    user = crud.getUserbyToken(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                            "token": "Your existing token is not valid !"})
    return user


@router.post("/user", response_model=schemas.UserRes)
async def newUser(user: schemas.UserCreat, db: Session = Depends(get_db)):
    validate = crud.get_user_by_data(db, username=user.username)
    if validate:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={
                            "username": "Username already exist !"})
    return crud.createUser(db, user)


@router.post("/login")
async def loGin(username: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_data(db, username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                            "username": "User credential is not exist !"})
    validate = crud.check_password(db, username, password)
    if not validate:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={
                            "username": "User credential is not exist !"})
    get_token = crud.create_jwt({'username': username})
    return {'user': user, 'access_token': get_token, 'token_type': 'bearer'}
