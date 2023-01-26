"""Main Application"""
from typing import List
import fastapi as _fastapi
import fastapi.security as _security

import sqlalchemy.orm as _orm
import services as _services  # pylint: disable=E0401
import schemas as _schemas  # pylint: disable=E0401

app = _fastapi.FastAPI()


@app.post("/api/users")
async def create_user(
    user: _schemas.UserCreate,
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    """
    Create a New User.

    Calling this function triggers get_user_by_email(), create_user() and
    create_token() from services.py.

        Args:
            user (schemas.UserCreate): User Object
            db (sqlalchemy.orm.Session): Database session

        Returns:
            Newly created user with JWT token
    """
    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already in use")

    user = await _services.create_user(user, db)

    return await _services.create_token(user)


@app.post("/api/token")
async def generate_token(
    form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    """
    Generates a new jwt token

    Calling this function triggers authenticate_user() and create_token() from services.py
    """
    user = await _services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise _fastapi.HTTPException(
            status_code=401, detail="Incorrect username or password"
        )

    return await _services.create_token(user)


@app.get("/api/users/me", response_model=_schemas.User)
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    """
    Get Current User

    Calling this function triggers get_current_user() from services.py
    """
    return user


@app.post("/api/leads", response_model=_schemas.Lead)
async def create_lead(
    lead: _schemas.LeadCreate,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    """
    Post new lead to the database

        calling this function triggers create_lead() from services.py


        params: lead (schemas.LeadCreate)
        params: user (schemas.User)
        params: db (sqlalchemy.orm.Session)

        returns: lead (schemas.Lead)
    """
    return await _services.create_lead(user=user, db=db, lead=lead)


@app.get("/api/leads", response_model=List[_schemas.Lead])
async def get_leads(
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    """
    Get a list of leads for a given user

        params: user (schemas.User)
        params: db (sqlalchemy.orm.Session)

        returns: List[schemas.Lead]
    """
    return await _services.get_leads(user=user, db=db)


@app.get("/api/leads/{lead_id}", status_code=200)
async def get_lead(
    lead_id: int,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    """
    Get a single lead by id

            params: lead_id (int)
            params: user (schemas.User)
            params: db (sqlalchemy.orm.Session)

            returns: lead (schemas.Lead)
    """
    return await _services.get_lead(lead_id, user, db)


@app.delete("/api/leads/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: int,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    """
    Delete a lead by id

            params: lead_id (int)
            params: user (schemas.User)
            params: db (sqlalchemy.orm.Session)

            returns: None
    """
    await _services.delete_lead(lead_id, user, db)
    return {"message", "Successfully Deleted"}


@app.put("/api/leads/{lead_id}", status_code=200)
async def update_lead(
    lead_id: int,
    lead: _schemas.LeadCreate,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    """
    Update a lead by id

            params: lead_id (int)
            params: lead (schemas.LeadCreate)
            params: user (schemas.User)
            params: db (sqlalchemy.orm.Session)

            returns: lead (schemas.Lead)
    """
    await _services.update_lead(lead_id, lead, user, db)
    return {"message", "Successfully Updated"}


@app.get("/api")
async def root():
    """
    Root url
    """
    return {"message": "Awesome Leads Manager"}
