import enum
from os import stat
from typing import Optional

from fastapi import FastAPI, Response, status, HTTPException
from fastapi.param_functions import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="santiago",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connection was successful.")
        break
    except Exception as error:
        print("Connecting to database failed.")
        print(f"Error: {error}")
        time.sleep(3)

    my_posts = [
        {"title": "title of post 1", "content": "content of post 1", "id": 1},
        {"title": "favorite foods", "content": "I like pizza", "id": 2},
    ]


def raise_404_not_found(id):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"post with ID {id} does not exist.",
    )


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


"""
Be careful when you create new paths, and check the order in which they're created, for example:

/posts/{id} being created before /posts/latests means that when we want to call "/posts/latest", "latest" will be used as a parameter for the first path, not the second, which leads to us never being able to call "/posts/latest".
"""


@app.get("/")
def root():
    return {"message": "Santiago's API"}


@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts;""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute(
        """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
        (post.title, post.content, post.published),
    )

    new_post = cursor.fetchone()

    conn.commit()

    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(
    id: int,
):
    cursor.execute("""SELECT * FROM posts WHERE id = %s;""", str(id))
    post = cursor.fetchone()
    if not post:
        raise_404_not_found(id)

    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *;""", str(id))

    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise_404_not_found(id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):

    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING*;""",
        (post.title, post.content, post.published, str(id)),
    )

    updated_post = cursor.fetchone()

    conn.commit()

    if updated_post == None:
        raise_404_not_found(id)

    return {"data": updated_post}
