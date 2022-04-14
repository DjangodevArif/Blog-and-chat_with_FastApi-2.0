from typing import Optional
import datetime
from sqlalchemy.orm import Session
from . import models, schemas

from passlib.context import CryptContext
from jose import JWTError, jwt

pass_manager = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "382098ceb4937a014ff1a33341c55d4052f1f1fefc6cc84dfcf7e6952afeea09"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def createUser(db: Session, user: schemas.UserCreat):
    hashed_password = pass_manager.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_data(db: Session, username: Optional[str] = None, id: Optional[str] = None):
    if username:
        return db.query(models.User).filter(models.User.username == username).first()
    elif id:
        return db.query(models.User).get(id)


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


def check_password(db: Session, username: str, password: str):
    userIndb = db.query(models.User).filter(
        models.User.username == username).first()
    check = pass_manager.verify(password, userIndb.password)
    return check


def create_jwt(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow(
    ) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    token = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return token


def getUserbyToken(db, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
    except JWTError as e:
        return None
    return get_user_by_data(db, username=payload['username'])
