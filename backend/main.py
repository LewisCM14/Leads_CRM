"""Main Application"""

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

    Calling this function triggers get_user_by_email() and create_user() from services.py

        Args:
            user (schemas.UserCreate): User Object
            db (sqlalchemy.orm.Session): Database session

        Returns:
            Newly created user
    """
    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already in use")
    return await _services.create_user(user, db)


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
