from functools import reduce

from sqlalchemy.orm import Mapped

from app.db.database import db, CRUDBase


class PaymentDocuments(db.Model, CRUDBase):
    """Модель для нормативных документов."""

    __tablename__ = "payment_documents"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.Text)
    increase: Mapped["PaymentIncrease"] = db.relationship(
        "PaymentIncrease",
        back_populates="document",
        cascade="save-update",
        lazy="subquery",
    )

    def __repr__(self):
        return self.name


class PaymentRates(db.Model, CRUDBase):
    """Модель базовых окладов."""

    __tablename__ = "payment_rates"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    slug: Mapped[str] = db.Column(db.String(64), index=True, unique=True)
    name: Mapped[str] = db.Column(db.String(128))
    payment_name: Mapped[str] = db.Column(db.String(128))
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
    values: Mapped[list["PaymentRatesValues"]] = db.relationship(
        "PaymentRatesValues",
        back_populates="rate",
        cascade="all, delete-orphan",
    )
    increase: Mapped[list["PaymentIncrease"]] = db.relationship(
        "PaymentIncrease",
        secondary="payment_match_rate_increase",
        back_populates="rates",
    )
    addons: Mapped[list["PaymentAddons"]] = db.relationship(
        "PaymentAddons",
        secondary="payment_match_rate_addon",
        back_populates="rates",
    )
    single_addons: Mapped[list["PaymentSingleAddons"]] = db.relationship(
        "PaymentSingleAddons",
        secondary="payment_match_rate_single",
        back_populates="rates",
    )

    def __repr__(self):
        return self.slug

    def get_increase_values(self) -> list:
        """Возвращает коэффициенты индексации для объекта."""
        return [increase.value for increase in self.increase]

    def get_current_values(self) -> dict:
        """Возвращает id и названия окладов по возрастанию."""

        return {
            item.id: item.name
            for item in sorted(self.values, key=lambda item: int(item.value))
        }

    def get_value_data(self, value_id):
        for item in self.values:
            if item.id == value_id:
                item.value = reduce(
                    lambda x, y: round(x * y + 0.5),
                    self.get_increase_values(),
                    item.value,
                )
                return item


class PaymentRatesValues(db.Model, CRUDBase):
    """Модель значений базовых окладов."""

    __tablename__ = "payment_rates_values"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[int] = db.Column(db.Integer)
    description: Mapped[str] = db.Column(db.Text)
    rate_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_rates.id"),
        nullable=False,
    )
    rate: Mapped[PaymentRates] = db.relationship(
        PaymentRates,
        back_populates="values",
        lazy="subquery",
    )
    document_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_documents.id", ondelete="SET NULL"),
    )
    document: Mapped[PaymentDocuments] = db.relationship(
        PaymentDocuments,
        lazy="joined",
    )

    def __repr__(self):
        return self.name


class PaymentAddons(db.Model, CRUDBase):
    """Модель коэффициентов дополнительных выплат к зарплате."""

    __tablename__ = "payment_addons"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    slug: Mapped[str] = db.Column(db.String(64), index=True, unique=True)
    name: Mapped[str] = db.Column(db.String(128))
    payment_name: Mapped[str] = db.Column(db.String(128))
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
    values: Mapped[list["PaymentAddonsValues"]] = db.relationship(
        "PaymentAddonsValues",
        back_populates="addon",
        cascade="all, delete-orphan",
    )
    rates: Mapped[list[PaymentRates]] = db.relationship(
        PaymentRates,
        secondary="payment_match_rate_addon",
        back_populates="addons",
    )

    def __repr__(self):
        return self.slug

    def get_values(self) -> dict:
        """Возвращает значения опций по возрастанию."""

        return {
            item.id: item.name
            for item in sorted(self.values, key=lambda item: float(item.value))
        }

    def get_value_data(self, value_id):
        for item in self.values:
            if item.id == value_id:
                return item


class PaymentAddonsValues(db.Model, CRUDBase):
    """Модель значений дополнительных выплат к зарплате."""

    __tablename__ = "payment_addons_values"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[float] = db.Column(db.Float)
    description: Mapped[str] = db.Column(db.Text)
    document_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_documents.id", ondelete="SET NULL"),
    )
    document: Mapped[PaymentDocuments] = db.relationship(
        PaymentDocuments,
        lazy="joined",
    )
    addon_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_addons.id"),
        nullable=False,
    )
    addon: Mapped[PaymentAddons] = db.relationship(
        "PaymentAddons",
        back_populates="values",
    )

    def __repr__(self):
        return self.name


class PaymentMatchRateAddon(db.Model):
    """Модель соотношения доп. выплат и окладов от которых они рассчитываются."""

    __tablename__ = "payment_match_rate_addon"
    __table_args__ = (db.UniqueConstraint("rate_id", "addon_id"),)
    rate_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_rates.id"),
        primary_key=True,
    )
    addon_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_addons.id"),
        primary_key=True,
    )


class PaymentSingleAddons(db.Model, CRUDBase):
    """Модель коэффициентов единичных надбавок к зарплате."""

    __tablename__ = "payment_single_addons"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    slug: Mapped[str] = db.Column(db.String(64), index=True, unique=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[float] = db.Column(db.Float)
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.Text)
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
    default_state: Mapped[bool] = db.Column(db.Boolean)
    document_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_documents.id", ondelete="SET NULL"),
    )
    document: Mapped[PaymentDocuments] = db.relationship(
        PaymentDocuments,
        lazy="joined",
    )
    rates: Mapped[list[PaymentRates]] = db.relationship(
        PaymentRates,
        secondary="payment_match_rate_single",
        back_populates="single_addons"
    )

    def __repr__(self):
        return self.slug


class PaymentMatchRateSingle(db.Model):
    """Модель соотношения доп. выплат и окладов."""

    __tablename__ = "payment_match_rate_single"
    __table_args__ = (db.UniqueConstraint("rate_id", "single_addon_id"),)
    rate_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_rates.id"),
        primary_key=True,
    )
    single_addon_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_single_addons.id"),
        primary_key=True,
    )


class PaymentIncrease(db.Model, CRUDBase):
    """Модель с данными об индексации окладов."""

    __tablename__ = "payment_increase"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[float] = db.Column(db.Float)
    document_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_documents.id", ondelete="SET NULL"),
    )
    document: Mapped[PaymentDocuments] = db.relationship(
        PaymentDocuments,
        back_populates="increase",
        lazy="joined",
    )
    rates: Mapped[list[PaymentRates]] = db.relationship(
        PaymentRates,
        secondary="payment_match_rate_increase",
        back_populates="increase",
    )

    def __repr__(self):
        return self.name


class PaymentMatchRateIncrease(db.Model):
    """Модель соотношения доп. выплат и окладов."""

    __tablename__ = "payment_match_rate_increase"
    __table_args__ = (db.UniqueConstraint("rate_id", "increase_id"),)
    rate_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_rates.id"),
        primary_key=True,
    )
    increase_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_increase.id"),
        primary_key=True,
    )


class PaymentPensionDutyCoefficient(db.Model, CRUDBase):
    """Модель понижающих пенсию коэффициентов за выслугу лет."""

    __tablename__ = "payment_pension_duty_coefficient"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[float] = db.Column(db.Float)
    document_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_documents.id", ondelete="SET NULL"),
    )
    document: Mapped[PaymentDocuments] = db.relationship(
        PaymentDocuments,
        lazy="joined",
    )

    def __repr__(self) -> str:
        return self.name


class PaymentGlobalCoefficient(db.Model, CRUDBase):
    """Модель глобальных коэффициентов, влияющих на общую сумму выплаты."""

    __tablename__ = "payment_global_coefficient"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    slug: Mapped[str] = db.Column(db.String(64), index=True, unique=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[float] = db.Column(db.Float)
    payment_name: Mapped[str] = db.Column(db.String(128))
    description: Mapped[str] = db.Column(db.Text)
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
    document_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_documents.id", ondelete="SET NULL"),
    )
    document: Mapped[PaymentDocuments] = db.relationship(
        PaymentDocuments,
        lazy="joined",
    )

    def __repr__(self) -> str:
        return self.name
