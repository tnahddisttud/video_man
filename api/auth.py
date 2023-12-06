from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import User
from schema.schemas import UserCreate, ShowUser
from services.hashing import Hasher
from jose import jwt
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

router = APIRouter()


@router.post("/login/token", tags=["Login"])
def retrieve_token_for_authenticated_user(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username"
        )
    if not Hasher.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password"
        )
    data = {"sub": form_data.username}
    jwt_token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    response.set_cookie(key="access_token", value=f"Bearer {jwt_token}", httponly=True)
    return {"access_token": jwt_token, "token_type": "bearer"}


@router.post("/user", tags=["User"], response_model=ShowUser)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user = User(email=user.email, password=Hasher.get_hash_password(user.password), role=user.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
