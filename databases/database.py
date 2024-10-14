from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine

from .config import settings


class Base1(DeclarativeBase):
    pass


sync_engine = create_engine(url=settings.DB_URL, echo=False)

session_factory = sessionmaker(sync_engine, expire_on_commit=False)
