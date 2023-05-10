from functools import reduce

from sqlalchemy import select
from sqlalchemy.orm import Mapped

from app.db.database import db


class PaymentBase:
    @classmethod
    def get_all(cls) -> list[db.Model]:
        return db.session.execute(select(cls)).scalars().all()


class PaymentRate(db.Model, PaymentBase):
    """Модель базовых окладов."""

    __tablename__ = "payment_rate"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    slug: Mapped[str] = db.Column(db.String(64), index=True, unique=True)
    name: Mapped[str] = db.Column(db.String(128))
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.String)
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
    values: Mapped[list["PaymentRateValues"]] = db.relationship(
        "PaymentRateValues",
        back_populates="rate",
        cascade="all, delete-orphan",
    )
    increase: Mapped[list["PaymentIncrease"]] = db.relationship(
        secondary="payment_match_rate_increase",
    )

    def __repr__(self):
        return self.slug

    def get_increase_values(self) -> list:
        """Возвращает коэффициенты индексации для объекта."""
        return [increase.value for increase in self.increase]

    def get_current_values(self) -> dict:
        """Возвращает значения с учетом индексации."""
        return {
            value.name: reduce(
                lambda x, y: round(x * y + 0.5), self.get_increase_values(), value.value
            )
            for value in self.values
        }


class PaymentRateValues(db.Model):
    """Модель значений базовых окладов."""

    __tablename__ = "payment_rate_values"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[int] = db.Column(db.Integer)
    rate_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_rate.id"),
        nullable=False,
    )
    rate: Mapped[PaymentRate] = db.relationship(
        "PaymentRate",
        back_populates="values",
        lazy="subquery",
    )


class PaymentPensionDutyCoefficient(db.Model, PaymentBase):
    """Модель понижающих пенсию коэффициентов за выслугу лет."""

    __tablename__ = "payment_pension_duty_coefficient"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[float] = db.Column(db.Float)
    description: Mapped[str] = db.Column(db.String)

    @classmethod
    def get_description(cls, name) -> dict:
        """Возвращает описание по имени."""

        return db.session.execute(select(cls).where(cls.name == name)).scalar_one_or_none()


class PaymentAddons(db.Model, PaymentBase):
    """Модель коэффициентов дополнительных выплат к зарплате."""

    __tablename__ = "payment_addons"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    slug: Mapped[str] = db.Column(db.String(64), index=True, unique=True)
    name: Mapped[str] = db.Column(db.String(128))
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.String)
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
    values: Mapped[list["PaymentAddonsValues"]] = db.relationship(
        "PaymentAddonsValues",
        back_populates="addon",
        cascade="all, delete-orphan",
    )
    rate: Mapped[list[PaymentRate]] = db.relationship(
        secondary="payment_match_rate_addon",
    )

    def __repr__(self):
        return self.slug

    def get_values(self) -> dict:
        """Возвращает значения опций."""

        return {option.name: option.value for option in self.values}


class PaymentAddonsValues(db.Model):
    """Модель значений дополнительных выплат к зарплате."""

    __tablename__ = "payment_addons_values"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[float] = db.Column(db.Float)
    addon_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_addons.id"),
        nullable=False,
    )
    addon: Mapped[PaymentAddons] = db.relationship(
        "PaymentAddons",
        back_populates="values",
        lazy="subquery",
    )


class PaymentMatchRateAddon(db.Model):
    """Модель соотношения доп. выплат и окладов от которых они рассчитываются."""

    __tablename__ = "payment_match_rate_addon"
    __table_args__ = (db.UniqueConstraint("rate_id", "addon_id"),)
    rate_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_rate.id"),
        primary_key=True,
    )
    addon_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_addons.id"),
        primary_key=True,
    )


class PaymentSingleAddon(db.Model, PaymentBase):
    """Модель коэффициентов единичных надбавок к зарплате."""

    __tablename__ = "payment_single_addon"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    slug: Mapped[str] = db.Column(db.String(64), index=True, unique=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[float] = db.Column(db.Float)
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.String)
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
    default_state: Mapped[bool] = db.Column(db.Boolean)
    rate: Mapped[list[PaymentRate]] = db.relationship(
        secondary="payment_match_rate_single",
    )

    def __repr__(self):
        return self.slug


class PaymentMatchRateSingle(db.Model):
    """Модель соотношения доп. выплат и окладов."""

    __tablename__ = "payment_match_rate_single"
    __table_args__ = (db.UniqueConstraint("rate_id", "single_addon_id"),)
    rate_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_rate.id"),
        primary_key=True,
    )
    single_addon_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_single_addon.id"),
        primary_key=True,
    )


class PaymentIncrease(db.Model):
    """Модель с данными об индексации окладов."""

    __tablename__ = "payment_increase"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[float] = db.Column(db.Float)
    description: Mapped[str] = db.Column(db.String)

    def __repr__(self):
        return self.name


class PaymentMatchRateIncrease(db.Model):
    """Модель соотношения доп. выплат и окладов."""

    __tablename__ = "payment_match_rate_increase"
    __table_args__ = (db.UniqueConstraint("rate_id", "payment_increase_id"),)
    rate_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_rate.id"),
        primary_key=True,
    )
    payment_increase_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_increase.id"),
        primary_key=True,
    )


class PaymentGlobalCoefficient(db.Model, PaymentBase):
    """Модель глобальных коэффициентов, влияющих на общую сумму выплаты."""

    __tablename__ = "payment_global_coefficient"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    slug: Mapped[str] = db.Column(db.String(64), index=True, unique=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[float] = db.Column(db.Float)
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.String)
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
