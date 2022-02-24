from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


def raise_404_not_found(id):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"post with ID {id} does not exist.",
    )


"""
Be careful when you create new paths, and check the order in which they're created, for example:

/posts/{id} being created before /posts/latests means that when we want to call "/posts/latest", "latest" will be used as a parameter for the first path, not the second, which leads to us never being able to call "/posts/latest".
"""


@router.get("/", response_model=List[schemas.Post])
def get_posts(
    db: Session = Depends(get_db),
    user_id: int = Depends(oauth2.get_current_user),
):
    posts = db.query(models.Post).all()

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(oauth2.get_current_user),
):
    print(user_id)
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=schemas.Post)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise_404_not_found(id)

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise_404_not_found(id)

    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    updated_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise_404_not_found(id)

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
