import asyncio
from base import ParseXML
from databases.queries.orm import SyncORM, SyncStartORM


async def main():
    SyncStartORM.create_tables()
    ParseXML().parse_to_database()

    print(f"10 лиц с наибольшим количеством обязательств:")
    for x in SyncORM.get_10_debtors_max_obligations():
        print(x)

    print()

    print("10 лиц с наибольшей общей суммой задолженностей:")
    for x in SyncORM.get_10_debtors_max_debt():
        print(x)

    print()

    print(
        "Все физические лица с процентом общей выплаченной суммы по всем обязательствам относительно общей суммы своих обязательств:"
    )
    for x in SyncORM.get_debtors_percentage():
        print(x)


if __name__ == "__main__":
    asyncio.run(main())
