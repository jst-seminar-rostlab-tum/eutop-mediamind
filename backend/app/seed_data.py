import asyncio

from app.core.db import seed_data


async def main():
    await seed_data()


if __name__ == "__main__":
    asyncio.run(main())
