"""Database Schema"""

import datetime as _dt
import pydantic as _pydantic


class _UserBase(_pydantic.BaseModel):
    """Base User Class"""

    email: str


class UserCreate(_UserBase):
    """Create a new user"""

    hashed_password: str

    class Config:
        """Config"""

        orm_mode = True


class User(_UserBase):
    """User"""

    id: int

    class Config:
        """Config"""

        orm_mode = True


class _LeadBase(_pydantic.BaseModel):
    """Base Lead Class"""

    first_name: str
    last_name: str
    email: str
    company: str
    note: str


class LeadCreate(_LeadBase):
    """Create a new lead"""

    pass


class Lead(_LeadBase):
    """Lead Schema"""

    id: int
    owner_id: int
    date_created: _dt.datetime
    date_last_updated: _dt.datetime

    class Config:
        """Config"""

        orm_mode = True
