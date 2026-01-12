from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import db


class StaffStableBusyTypes(db.Model):
    """Модель для типов занятости постоянного состава."""

    __tablename__ = "staff_stable_busy_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class StaffVariousBusyTypes(db.Model):
    """Модель для типов занятости переменного состава."""
    __tablename__ = "staff_various_busy_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String)
    match: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class StaffVariousIllnessTypes(db.Model):
    """Модель для разновидностей болезней переменного состава."""
    __tablename__ = "staff_various_illness_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class StaffAllowedFaculty(db.Model):
    """Модель факультетов для которых собираются данные."""
    __tablename__ = "staff_allowed_faculty"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apeks_id: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String)
    short_name: Mapped[str] = mapped_column(String)
    sort: Mapped[int] = mapped_column(Integer)
    branch_id: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    
