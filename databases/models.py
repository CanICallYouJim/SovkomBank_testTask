import datetime
import uuid
from typing import Annotated
from sqlalchemy import *
import enum

from .database import Base1
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

pk_int = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
pk_uuid = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]
bm_id_fk = Annotated[
    uuid.UUID,
    mapped_column(
        ForeignKey(
            "extra_judicial_bankruptcy_message.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        )
    ),
]
num = Annotated[int, mapped_column(Numeric(scale=2))]


class ExtrajudicialBankruptcyMessage(Base1):
    __tablename__ = "extra_judicial_bankruptcy_message"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(BigInteger())
    type: Mapped[str]
    publish_date: Mapped[datetime.datetime]
    finish_reason: Mapped[str | None]

    debtor_instance: Mapped["Debtor"] = relationship(
        back_populates="bankruptcy_message_instance"
    )
    monetary_obligations_instances: Mapped[list["MonetaryObligation"]] = relationship(
        back_populates="bankruptcy_message_instance"
    )


class Debtor(Base1):
    __tablename__ = "debtors"

    id: Mapped[pk_uuid]
    name: Mapped[str]
    birth_date: Mapped[datetime.datetime]
    birth_place: Mapped[str]
    address: Mapped[str]
    inn: Mapped[int | None] = mapped_column(BigInteger(), unique=True)
    extra_judicial_bankruptcy_message: Mapped[bm_id_fk]

    bankruptcy_message_instance: Mapped["ExtrajudicialBankruptcyMessage"] = (
        relationship(back_populates="debtor_instance")
    )


class Bank(Base1):
    __tablename__ = "banks"

    id: Mapped[pk_uuid]
    name: Mapped[str]
    bik: Mapped[int | None] = mapped_column(BigInteger())
    extra_judicial_bankruptcy_message: Mapped[bm_id_fk]


class MonetaryObligation(Base1):
    __tablename__ = "monetary_obligations"

    id: Mapped[pk_uuid]
    creditor_name: Mapped[str]
    content: Mapped[str]
    basis: Mapped[str]
    total_sum: Mapped[num]
    debt_sum: Mapped[num] = mapped_column(default=text("0"))
    extra_judicial_bankruptcy_message: Mapped[bm_id_fk]

    bankruptcy_message_instance: Mapped["ExtrajudicialBankruptcyMessage"] = (
        relationship(back_populates="monetary_obligations_instances")
    )


class ObligatoryPayment(Base1):
    __tablename__ = "obligatory_payments"

    id: Mapped[pk_uuid]
    name: Mapped[str]
    sum: Mapped[num]
    extra_judicial_bankruptcy_message: Mapped[bm_id_fk]


class Publisher(Base1):
    __tablename__ = "publishers"

    id: Mapped[pk_uuid]
    name: Mapped[str]
    inn: Mapped[int] = mapped_column(BigInteger())
    ogrn: Mapped[int] = mapped_column(BigInteger())
    extra_judicial_bankruptcy_message: Mapped[bm_id_fk]
