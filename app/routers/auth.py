from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from app import utils
from .. import database, schemas, models, oauth2

router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials"
        )

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials"
        )

    # In here I could put the role and everything else I want inside the dictionary, but this will do for now.
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
