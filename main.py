from typing import Optional

from fastapi import FastAPI
from fastapi.param_functions import Body
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


@app.get("/")
def root():
    return {"message": "Santiago's API"}


@app.get("/posts")
def get_posts():
    return {"data": "These are your posts!"}


@app.post("/createposts")
def create_posts(post: Post):
    print(post)
    print(post.dict())
    return {"data": post}
