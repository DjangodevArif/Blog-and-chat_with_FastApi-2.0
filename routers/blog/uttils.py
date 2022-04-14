from sqlite3 import DataError
from sqlalchemy.orm.session import Session
from routers.blog.schemas import CreateFeed, CreateComment, CreateReaction, CreateReply
from routers.blog.models import Feed, Comment, Reaction, Reply


def create_post(db: Session, user_id: int, post: CreateFeed):
    post = Feed(**post.dict(), user_id=user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def create_comment(db: Session, feed_id: int, user_id: int, comment: CreateComment):
    comment = Comment(**comment.dict(), user_id=user_id, feed_id=feed_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def create_reply(db: Session, reply: CreateReply, user_id: int):
    reply = Reply(**reply.dict(), user_id=user_id)
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply

# , offset: int, limit: int


def get_feed_comment(db: Session, feed_id: int, offset: int, limit: int):
    list_of_comment = db.query(Comment).filter(Comment.feed_id == feed_id).order_by(
        Comment.id.desc()).offset(offset).limit(limit).all()
    return list_of_comment


def add_or_remove_feed_react(db: Session, feed_id: int, user_id: int, react: CreateReaction):
    is_exiist = db.query(Reaction).filter(
        Reaction.feed_id == feed_id, Reaction.user_id == user_id).first()
    if is_exiist:
        item = db.query(Reaction).filter(Reaction.feed_id ==
                                         feed_id, Reaction.user_id == user_id).one()
        db.delete(item)
        db.commit()
        fetch = db.query(Reaction).filter(Reaction.feed_id == feed_id).all()
        return fetch
    else:
        react = Reaction(**react.dict(), user_id=user_id, feed_id=feed_id)
        db.add(react)
        db.commit()
        db.refresh(react)
        fetch = db.query(Reaction).filter(Reaction.feed_id == feed_id).all()
        return fetch
        # except Exception as e:
        #     return e
