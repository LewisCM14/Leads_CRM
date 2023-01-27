"""Backend Service Functions"""

import datetime as _dt
import os

import database as _database  # pylint: disable=E0401
import fastapi as _fastapi
import fastapi.security as _security
import jwt as _jwt
import models as _models  # pylint: disable=E0401
import passlib.hash as _hash
import schemas as _schemas  # pylint: disable=E0401
import sqlalchemy.orm as _orm
from dotenv import load_dotenv

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
        raise _fastapi.HTTPException(  # pylint: disable=W0707
            status_code=401, detail="Invalid Email or Password"
        )

    return _schemas.User.from_orm(user)


async def create_lead(user: _schemas.User, db: _orm.Session, lead: _schemas.LeadCreate):
    """
    Create a new lead and commit to database

        param user: User to create lead for
        param db: Database connection
        param lead: Lead to create
    """
    lead = _models.Lead(**lead.dict(), owner_id=user.id)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return _schemas.Lead.from_orm(lead)


async def get_leads(user: _schemas.User, db: _orm.Session):
    """
    Get Leads

        :param user: User to filter leads by
        :param db: Database session
        :return: A list of leads from database
    """
    leads = db.query(_models.Lead).filter_by(owner_id=user.id)
    return list(map(_schemas.Lead.from_orm, leads))


async def _lead_selector(lead_id: int, user: _schemas.User, db: _orm):
    """
    A helper function to select a specific lead from the database

        :param lead_id: (int): Lead ID to filter by
        :param user: User to filter leads by
        :param db: Database session

        return: A lead
    """
    lead = db.query(_models.Lead).filter_by(id=lead_id, owner_id=user.id).first()
    if not lead:
        raise _fastapi.HTTPException(
            status_code=404, detail="A lead matching these details does not exist"
        )
    return lead


async def get_lead(lead_id: int, user: _schemas.User, db: _orm.Session):
    """
    Get Lead, this function calls the _lead_selector()

        :param lead_id: (int): Lead ID
        :param user: User
        :param db: Database session

        return: A ORM mapped lead
    """

    lead = await _lead_selector(lead_id=lead_id, user=user, db=db)
    return _schemas.Lead.from_orm(lead)


async def delete_lead(lead_id: int, user: _schemas.User, db: _orm.Session):
    """
    Delete Lead from the database, this function calls the _lead_selector()

        :param lead_id: (int): Lead ID
        :param user: User
        :param db: Database session

        return: None
    """
    lead = await _lead_selector(lead_id, user, db)

    db.delete(lead)
    db.commit()


async def update_lead(
    lead_id: int, lead: _schemas.LeadCreate, user: _schemas.User, db: _orm.Session
):
    """
    Update Lead, this function calls the _lead_selector()

        :param lead_id: (int): Lead ID
        :param lead: Lead to update, date update done server-side
        :param user: User
        :param db: Database session

        return: A ORM mapped lead
    """
    lead_db = await _lead_selector(lead_id, user, db)

    lead_db.first_name = lead.first_name
    lead_db.last_name = lead.last_name
    lead_db.email = lead.email
    lead_db.company = lead.company
    lead_db.note = lead.note
    lead_db.date_last_updated = _dt.datetime.utcnow()

    db.commit()
    db.refresh(lead_db)

    return _schemas.Lead.from_orm(lead_db)
