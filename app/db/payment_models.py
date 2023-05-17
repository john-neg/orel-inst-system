from functools import reduce

from sqlalchemy import select
from sqlalchemy.orm import Mapped

from app.db.database import db


class PaymentBase:
    """Базовый класс для приложения Payments."""

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get(cls, id_) -> db.Model:
        """Возвращает объект по id."""

        return db.session.execute(select(cls).where(cls.id == id_)).scalar_one_or_none()

    @classmethod
    def get_all(cls) -> list[db.Model]:
        return db.session.scalars(select(cls)).all()

    @classmethod
    def create(cls, **kwargs) -> db.Model:
        db_obj = cls(**kwargs)
        db.session.add(db_obj)
        db.session.commit()
        return cls.get(db_obj.id)

    @classmethod
    def update(cls, id_, **kwargs) -> db.Model:
        db_obj = cls.get(id_)
        for column, value in kwargs.items():
            setattr(db_obj, column, value)
        db.session.commit()
        return db_obj

    @classmethod
    def delete(cls, id_) -> str:
        db_obj = cls.get(id_)
        db.session.delete(db_obj)
        db.session.commit()
        return f"Запись '{db_obj}' удалена"


class PaymentDocuments(db.Model, PaymentBase):
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


class PaymentRate(db.Model, PaymentBase):
    """Модель базовых окладов."""

    __tablename__ = "payment_rate"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    slug: Mapped[str] = db.Column(db.String(64), index=True, unique=True)
    name: Mapped[str] = db.Column(db.String(128))
    payment_name: Mapped[str] = db.Column(db.String(128))
    salary: Mapped[bool] = db.Column(db.Boolean)
    pension: Mapped[bool] = db.Column(db.Boolean)
    values: Mapped[list["PaymentRateValues"]] = db.relationship(
        "PaymentRateValues",
        back_populates="rate",
        cascade="all, delete-orphan",
    )
    increase: Mapped[list["PaymentIncrease"]] = db.relationship(
        "PaymentIncrease",
        secondary="payment_match_rate_increase",
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


class PaymentRateValues(db.Model):
    """Модель значений базовых окладов."""

    __tablename__ = "payment_rate_values"
    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = db.Column(db.String(128))
    value: Mapped[int] = db.Column(db.Integer)
    description: Mapped[str] = db.Column(db.Text)
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
    document_id: Mapped[int] = db.Column(
        db.Integer,
        db.ForeignKey("payment_documents.id", ondelete="SET NULL"),
    )
    document: Mapped[PaymentDocuments] = db.relationship(
        PaymentDocuments,
        lazy="subquery",
    )

    def __repr__(self):
        return self.name


class PaymentAddons(db.Model, PaymentBase):
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
    rate: Mapped[list[PaymentRate]] = db.relationship(
        secondary="payment_match_rate_addon",
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


class PaymentAddonsValues(db.Model):
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
        lazy="subquery",
    )
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

    def __repr__(self):
        return self.name


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
        lazy="subquery",
    )
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


class PaymentIncrease(db.Model, PaymentBase):
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
        # passive_deletes=True,
        lazy="subquery",
    )
    rates: Mapped[list[PaymentRate]] = db.relationship(
        PaymentRate,
        secondary="payment_match_rate_increase",
        back_populates="increase",
        lazy='subquery'
    )

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


class PaymentPensionDutyCoefficient(db.Model, PaymentBase):
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
        lazy="subquery",
    )

    def __repr__(self) -> str:
        return self.name


class PaymentGlobalCoefficient(db.Model, PaymentBase):
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
        lazy="subquery",
    )
