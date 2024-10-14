from databases.database import sync_engine, session_factory
from databases.models import *


class SyncORM:

    @staticmethod
    def add_to_model(instances: list):
        with session_factory() as session:
            session.add_all(instances)
            session.commit()

    @staticmethod
    def get_10_debtors_max_obligations():
        with session_factory() as session:
            query = (
                select(Debtor.name, Debtor.inn, func.count("*"))
                .where(
                    Debtor.extra_judicial_bankruptcy_message
                    == MonetaryObligation.extra_judicial_bankruptcy_message
                )
                .group_by(Debtor.id)
                .order_by(
                    func.count(MonetaryObligation.id).desc()
                )  # Сортировка по количеству обязательств
                .limit(10)
            )
            res = session.execute(query)
            return res.all()

    @staticmethod
    def get_10_debtors_max_debt():
        with session_factory() as session:
            query = (
                select(
                    Debtor.name,
                    Debtor.inn,
                    cast(func.sum(MonetaryObligation.debt_sum), Float),
                )
                .where(
                    (
                        Debtor.extra_judicial_bankruptcy_message
                        == MonetaryObligation.extra_judicial_bankruptcy_message
                    )
                    & (MonetaryObligation.debt_sum.is_not(None))
                )
                .group_by(Debtor.id)
                .order_by(
                    func.sum(MonetaryObligation.debt_sum).desc()
                )  # Сортировка по количеству обязательств
                .limit(10)
            )
            res = session.execute(query)
            return res.all()

    @staticmethod
    def get_debtors_percentage():
        with session_factory() as session:
            query = (
                select(
                    Debtor.name,
                    Debtor.inn,
                    cast(
                        func.round(
                            (
                                func.sum(
                                    case((MonetaryObligation.debt_sum > 0, 1), else_=0)
                                )
                                / func.count(MonetaryObligation.id)
                                * 100
                            ),
                            2,
                        ),
                        Float,
                    ),
                )
                .where(
                    (
                        Debtor.extra_judicial_bankruptcy_message
                        == MonetaryObligation.extra_judicial_bankruptcy_message
                    )
                )
                .group_by(Debtor.id)
                .order_by(
                    func.round(
                        (
                            func.sum(
                                case((MonetaryObligation.debt_sum > 0, 1), else_=0)
                            )
                            / func.count(MonetaryObligation.id)
                            * 100
                        ),
                        2,
                    ).desc()
                )
            )  # Сортировка по количеству обязательств

            res = session.execute(query)
            return res.all()


class SyncStartORM:
    @staticmethod
    def create_tables():
        Base1.metadata.drop_all(sync_engine)
        Base1.metadata.create_all(sync_engine)
