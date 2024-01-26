from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .database import db


class StaffStableBusyTypes(db.Model):
    __tablename__ = 'staff_stable_busy_types'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class StaffVariousBusyTypes(db.Model):
    __tablename__ = 'staff_various_busy_types'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class StaffVariousIllnessTypes(db.Model):
    __tablename__ = 'staff_various_illness_types'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
