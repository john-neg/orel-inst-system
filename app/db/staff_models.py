from sqlalchemy import Date
from sqlalchemy.orm import Mapped
from sqlalchemy.types import DateTime

from app.db.auth_models import User
from app.db.database import db, CRUDBase


class StaffOperations(db.Model, CRUDBase):

    __tablename__ = "staff_operations"
    name: Mapped[str] = db.Column(db.Text)


class StaffOperationsJournal(db.Model, CRUDBase):

    __tablename__ = "staff_operations_journal"
    name: Mapped[str] = db.Column(db.Text)
    user_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    user: Mapped[User] = db.relationship(
        User,
        lazy="joined",
    )
    operation_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("staff_operations.id"),
        nullable=False,
    )
    time: Mapped[DateTime] = db.Column(db.DateTime)


class StaffBusyTypes(db.Model, CRUDBase):

    __tablename__ = "staff_busy_types"
    name: Mapped[str] = db.Column(db.Text)


class StaffBusyJournal(db.Model, CRUDBase):

    __tablename__ = "staff_busy_journal"
    staff_id: Mapped[int] = db.Column(
        db.Integer,
        nullable=False,
    )
    date: Mapped[Date] = db.Column(db.Date)
    busy_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("staff_busy_types.id"),
        nullable=False,
    )
    busy: Mapped[StaffBusyTypes] = db.relationship(
        StaffBusyTypes,
        lazy="joined",
    )
    description: Mapped[str] = db.Column(db.Text)

