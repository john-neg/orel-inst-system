from sqlalchemy.orm import Mapped

from app.db.database import db


class PaymentBase(db.Model):
    """Модель базовых окладов."""

    __tablename__ = "payment_base"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True, unique=True)
    values: Mapped[list["PaymentBaseValues"]] = db.relationship(
        "PaymentBaseValues",
        back_populates="base",
    )
    description: Mapped[str] = db.Column(db.String)


class PaymentBaseValues(db.Model):
    """Модель значений базовых окладов."""

    __tablename__ = "payment_base_values"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True, unique=True)
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


class PaymentDutyCoefficients(db.Model):
    """Модель увеличивающих зарплату коэффициентов за выслугу лет."""

    __tablename__ = "payment_duty_coefficients"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True, unique=True)
    value: Mapped[float] = db.Column(db.Float)


class PaymentDutyCoefficientPension(db.Model):
    """Модель понижающих пенсию коэффициентов за выслугу лет."""

    __tablename__ = "payment_duty_coefficient_pension"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True, unique=True)
    value: Mapped[float] = db.Column(db.Float)


class PaymentAddons(db.Model):
    """Модель коэффициентов дополнительных выплат к зарплате."""

    __tablename__ = "payment_addons"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True, unique=True)
    values: Mapped[list["PaymentAddonsValues"]] = db.relationship(
        "PaymentAddonsValues",
        back_populates="type",
    )
    base: Mapped[list[PaymentBase]] = db.relationship(
        secondary="payment_match_base_addon",
    )
    description: Mapped[str] = db.Column(db.String)


class PaymentAddonsValues(db.Model):
    """Модель значений дополнительных выплат к зарплате."""

    __tablename__ = "payment_addons_values"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128), index=True, unique=True)
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
    name: Mapped[str] = db.Column(db.String(128), index=True, unique=True)
    value: Mapped[float] = db.Column(db.Float)
    base: Mapped[list[PaymentBase]] = db.relationship(
        secondary="payment_match_base_single",
    )
    description: Mapped[str] = db.Column(db.String)


class PaymentMatchBaseSingle(db.Model):
    """Модель соотношения доп. выплат и окладов."""

    __tablename__ = "payment_match_base_single"
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
    value: Mapped[float] = db.Column(db.Float)
    base: Mapped[list[PaymentBase]] = db.relationship(
        secondary="payment_match_base_increase",
    )
    description: Mapped[str] = db.Column(db.String)


class PaymentMatchBaseIncrease(db.Model):
    """Модель соотношения доп. выплат и окладов."""

    __tablename__ = "payment_match_base_increase"
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
    name: Mapped[str] = db.Column(db.String(128), index=True, unique=True)
    value: Mapped[float] = db.Column(db.Float)
    description: Mapped[str] = db.Column(db.String)
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
