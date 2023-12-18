from sqlalchemy import Integer, Date
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date

from ..db.database import db


class ProductionCalendarHolidays(db.Model):
    __tablename__ = "production_calendar_holidays"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)

    def __repr__(self):
        return self.date.strftime("%Y-%m-%d")


class ProductionCalendarWorkingDays(db.Model):
    __tablename__ = "production_calendar_working_days"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)

    def __repr__(self):
        return self.date.strftime("%Y-%m-%d")
