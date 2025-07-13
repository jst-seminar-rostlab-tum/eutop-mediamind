import asyncio

from app.services.seeding_service.seeding_service import seed_data


async def main():
    await seed_data()


if __name__ == "__main__":
    asyncio.run(main())
