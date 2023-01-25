"""Backend Service Functions"""

import os
from dotenv import load_dotenv

import fastapi as _fastapi
import fastapi.security as _security
import database as _database  # pylint: disable=E0401
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import jwt as _jwt
import models as _models  # pylint: disable=E0401
import schemas as _schemas  # pylint: disable=E0401

load_dotenv()
oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")


def create_database():
    """Create Database"""

    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    """Get Database and Close Connection"""
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_email(email: str, db: _orm.Session):
    """
    Get User By Email

        :param email: (str): Email
        :param db: Database session
        :return: User from database filtered by email or None if not found
    """
    return db.query(_models.User).filter(_models.User.email == email).first()


async def create_user(user: _schemas.UserCreate, db: _orm.Session):
    """
    Create User, using passlib to hash password.

        :param user: User to create
        :param db: Database session
        :return: Created User, committed to database
    """
    user_obj = _models.User(
        email=user.email, hashed_password=_hash.bcrypt.hash(user.hashed_password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(email: str, password: str, db: _orm.Session):
    """
    Authenticate User

        This function calls the verify_password found in models.py

        :param email: (str): Email
        :param password: (str): Password
        :param db: Database session

        :return: User from database if authenticated
    """
    user = await get_user_by_email(email, db)
    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


async def create_token(user: _models.User):
    """
    Create Token with jwt

        :param user: User to create token for
        :return: Created dict with token and type
    """
    user_obj = _schemas.User.from_orm(user)
    token = _jwt.encode(user_obj.dict(), os.getenv("JWT_SECRET"))

    return dict(access_token=token, token_type="bearer")


async def get_current_user(
    db: _orm.Session = _fastapi.Depends(get_db),
    token: str = _fastapi.Depends(oauth2schema),
):
    """
    Get Current User

        :param db: Database session
        :param token: JWT Token
        :return: User from database
    """
    try:
        payload = _jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except:
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid Email or Password"
        )

    return _schemas.User.from_orm(user)
