import os

import discord, asyncpg, asyncio
from discord.ext import commands
from utils.caching.prefix_util import PrefixHelper


def get_prefix(bot, message):
    return bot.prefix[message.guild.id]


class EmojiBot(commands.Bot):
    __slots__: tuple[str, str] = ("prefix", "pool")

    async def on_ready(self):
        print(f"Successfully logged in as {self.user}")


async def main(bot):
    async with bot:
        bot.pool = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
        bot.prefix = await PrefixHelper(
            fetch="SELECT * FROM prefixes",
            write="INSERT INTO prefixes VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
            pool=bot.pool,
        )
        print(bot.prefix)
        await bot.start(os.getenv("DISCORD_TOKEN"))


bot = EmojiBot(command_prefix=get_prefix, intents=discord.Intents.all())


@bot.command()
async def prefix(ctx):
    return await ctx.send(bot.prefix[ctx.guild.id])


if __name__ == "__main__":
    asyncio.run(main(bot))
