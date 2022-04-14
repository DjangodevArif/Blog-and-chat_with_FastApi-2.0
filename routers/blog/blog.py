from typing import List
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import Response
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from routers.blog.models import Feed
from routers.blog.uttils import add_or_remove_feed_react, create_post, create_comment, create_reply, get_feed_comment
from routers.blog.schemas import CreateFeed, CreateReaction, CreateReply, ResFeed, ResComment, CreateComment, ResReaction, ResReply
from routers.users.crud import getUserbyToken
from dependencies import get_db, getAuthenticity


router = APIRouter(tags=["blog"])


@router.get("/feeds", response_model=List[ResFeed], status_code=status.HTTP_202_ACCEPTED)
async def get_feed(db: Session = Depends(get_db)):
    feeds = db.query(Feed).order_by(Feed.timestamp.desc()).all()
    return feeds


@router.post("/new_feed", response_model=ResFeed, status_code=status.HTTP_201_CREATED)
async def new_post(post: CreateFeed, db: Session = Depends(get_db), token: str = Depends(getAuthenticity)):
    current_user = getUserbyToken(db, token)
    add_post = create_post(db,  current_user.id, post)
    return add_post
    # return Response(content=jsonable_encoder(add_post), status_code=status.HTTP_201_CREATED)
    # return Response(content=add_post, status_code=status.HTTP_201_CREATED)


@router.get("/{feed_id}/comment", response_model=List[ResComment], status_code=status.HTTP_201_CREATED)
async def get_comment(feed_id: int, db: Session = Depends(get_db), token: str = Depends(getAuthenticity), offset: int = 0, limit: int = 10):
    comment = get_feed_comment(db, feed_id, offset, limit)
    return comment


@router.post("/{feed_id}/new_comment", response_model=ResComment, status_code=status.HTTP_201_CREATED)
async def new_comment(feed_id: int, comment: CreateComment, db: Session = Depends(get_db), token: str = Depends(getAuthenticity)):
    current_user = getUserbyToken(db, token)
    add_comment = create_comment(db, feed_id, current_user.id, comment)
    return add_comment


@router.post("/{feed_id}/reply", response_model=List[ResComment], status_code=status.HTTP_202_ACCEPTED)
async def new_reply(feed_id: int, reply: CreateReply, db: Session = Depends(get_db), token: str = Depends(getAuthenticity), offset: int = 0, limit: int = 10):
    current_user = getUserbyToken(db, token)
    add_reply = create_reply(db, reply, current_user.id)
    response = get_feed_comment(db, feed_id, offset, limit)
    return response


# response_model=ResReaction,
@router.post("/{feed_id}/reaction", response_model=List[ResReaction], status_code=status.HTTP_202_ACCEPTED)
async def react_feed(feed_id: int, react: CreateReaction, db: Session = Depends(get_db), token: str = Depends(getAuthenticity)):
    current_user = getUserbyToken(db, token)
    action = add_or_remove_feed_react(db, feed_id, current_user.id, react)
    return action
