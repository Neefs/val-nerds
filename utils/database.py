from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import asyncpg


load_dotenv(".env")
DB_IP = os.getenv("DB_IP")
DB_USER = os.getenv("DB_USER")
DB_PWD = os.getenv("DB_PWD")
DB_DATABASE = os.getenv("DB_DATABASE")

class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def get_pool():
        kwargs = {
            "host": DB_IP,
            "port": 5432,
            "user": DB_USER,
            "password": DB_PWD,
            "loop": asyncio.get_event_loop(),
            "database": DB_DATABASE
        }
        return await asyncpg.create_pool(**kwargs)

    async def cog_load(self) -> None:
        Database.pool= await self.get_pool()
        await self.init_tables()
        
        return await super().cog_load()

    async def cog_unload(self) -> None:
        await Database.pool.close()
        return await super().cog_unload()

    def format_json(self, record:asyncpg.Record):
        if record is None:
            return None
        return {key: value for (key, value) in dict(record).items()}

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.success(f'{self.__class__.__name__} cog is ready!')




    async def init_tables(self) -> None:
        async with self.pool.acquire() as conn:
            conn:asyncpg.Connection
            #CREATE TABLES HERE
            #await conn.execute("")


        



async def setup(bot):
    db = Database(bot)
    bot.db = db
    await bot.add_cog(db)
