from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class DefaultBase(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=DefaultBase)
