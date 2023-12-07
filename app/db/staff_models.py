from sqlalchemy import Date, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime

from ..db.auth_models import Users
from ..db.database import db


class StaffOperations(db.Model):
    __tablename__ = "staff_operations"
    name: Mapped[str] = mapped_column(Text)


class StaffOperationsJournal(db.Model):
    __tablename__ = "staff_operations_journal"
    name: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    user: Mapped[Users] = relationship(
        Users,
        lazy="joined",
    )
    operation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("staff_operations.id"),
        nullable=False,
    )
    time: Mapped[DateTime] = mapped_column(DateTime)


class StaffBusyTypes(db.Model):
    __tablename__ = "staff_busy_types"
    name: Mapped[str] = mapped_column(Text)


class StaffBusyJournal(db.Model):
    __tablename__ = "staff_busy_journal"
    staff_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    date: Mapped[Date] = mapped_column(Date)
    busy_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("staff_busy_types.id"),
        nullable=False,
    )
    busy: Mapped[StaffBusyTypes] = relationship(
        StaffBusyTypes,
        lazy="joined",
    )
    description: Mapped[str] = mapped_column(Text)
