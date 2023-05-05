from sqlalchemy.orm import Mapped

from app.db.database import db


class PaymentBase(db.Model):
    """Модель базовых окладов."""

    __tablename__ = "payment_base"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True)
    values: Mapped[list["PaymentBaseValues"]] = db.relationship(
        "PaymentBaseValues",
        back_populates="base",
        cascade="all, delete-orphan",
    )
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.String)


class PaymentBaseValues(db.Model):
    """Модель значений базовых окладов."""

    __tablename__ = "payment_base_values"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True)
    value: Mapped[int] = db.Column(db.Integer)
    base_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_base.id"),
        nullable=False,
    )
    base: Mapped[PaymentBase] = db.relationship(
        "PaymentBase",
        back_populates="values",
        lazy="subquery",
    )


class PaymentPensionDutyCoefficient(db.Model):
    """Модель понижающих пенсию коэффициентов за выслугу лет."""

    __tablename__ = "payment_pension_duty_coefficient"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True)
    value: Mapped[float] = db.Column(db.Float)


class PaymentAddons(db.Model):
    """Модель коэффициентов дополнительных выплат к зарплате."""

    __tablename__ = "payment_addons"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True)
    values: Mapped[list["PaymentAddonsValues"]] = db.relationship(
        "PaymentAddonsValues",
        back_populates="addon",
        cascade="all, delete-orphan",
    )
    base: Mapped[list[PaymentBase]] = db.relationship(
        secondary="payment_match_base_addon",
    )
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.String)


class PaymentAddonsValues(db.Model):
    """Модель значений дополнительных выплат к зарплате."""

    __tablename__ = "payment_addons_values"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True)
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


class PaymentMatchBaseAddon(db.Model):
    """Модель соотношения доп. выплат и окладов от которых они рассчитываются."""

    __tablename__ = "payment_match_base_addon"
    __table_args__ = (
        db.UniqueConstraint('base_id', 'addon_id'),
    )
    base_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_base.id"),
        primary_key=True,
    )
    addon_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_addons.id"),
        primary_key=True,
    )


class PaymentSingleAddon(db.Model):
    """Модель коэффициентов единичных надбавок к зарплате."""

    __tablename__ = "payment_single_addon"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True)
    value: Mapped[float] = db.Column(db.Float)
    base: Mapped[list[PaymentBase]] = db.relationship(
        secondary="payment_match_base_single",
    )
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.String)
    default_state: Mapped[bool] = db.Column(db.Boolean)


class PaymentMatchBaseSingle(db.Model):
    """Модель соотношения доп. выплат и окладов."""

    __tablename__ = "payment_match_base_single"
    __table_args__ = (
        db.UniqueConstraint('base_id', 'single_addon_id'),
    )
    base_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_base.id"),
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
    name: Mapped[str] = db.Column(db.String(128), index=True)
    value: Mapped[float] = db.Column(db.Float)
    base: Mapped[list[PaymentBase]] = db.relationship(
        secondary="payment_match_base_increase",
    )
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.String)


class PaymentMatchBaseIncrease(db.Model):
    """Модель соотношения доп. выплат и окладов."""

    __tablename__ = "payment_match_base_increase"
    __table_args__ = (
        db.UniqueConstraint('base_id', 'payment_increase_id'),
    )
    base_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_base.id"),
        primary_key=True,
    )
    payment_increase_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_increase.id"),
        primary_key=True,
    )


class PaymentGlobalCoefficient(db.Model):
    """Модель глобальных коэффициентов, влияющих на всю сумму выплаты."""

    __tablename__ = "payment_global_coefficient"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True)
    value: Mapped[float] = db.Column(db.Float)
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.String)
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
