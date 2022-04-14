
from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from dependencies import RoomEventMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from routers.users import users
from routers.blog import blog
from routers.chat import chat
from database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(users.router, prefix="/user")
app.include_router(chat.router, prefix="/chat")
app.include_router(blog.router, prefix="/feed")


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: HTTPException):
    error_body = {}
    for error in exc.errors():
        try:
            error_body[f"{error.get('loc')[1]}"] = str(
                error.get('msg')).capitalize()
        except:
            error_body[f"{error.get('loc')[0]}"] = str(
                error.get('msg')).capitalize()
    error_body['request_body'] = jsonable_encoder(exc.body)
    return JSONResponse({"error": error_body}, status_code=status.HTTP_400_BAD_REQUEST)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    RoomEventMiddleware
)
