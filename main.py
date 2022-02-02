import discord
import os
import asyncpg
from discord.ext import commands, tasks
from tools.database_tools import confirm_tables
from tools.bot_tools import get_default_prefix, get_mobile
from tools.enum_tools import TableType
from tools.caching_table_tools import Tables


discord.gateway.DiscordWebSocket.identify = (
    get_mobile()
)  # Remove this line if bot isn't working, experimental thing
DEFAULT_PREFIX = get_default_prefix()

# Get custom prefix for the guild
# Handle if not used in guild
async def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)

    # Actually in a guild
    query = "SELECT prefix FROM guilds WHERE guild_id = $1"
    prefix = await bot.db.fetch(query, message.guild.id)

    if len(prefix) == 0:
        query = "INSERT INTO guilds (guild_id, prefix) VALUES ($1, $2)"
        await bot.db.execute(query, message.guild.id, DEFAULT_PREFIX)
        prefix = DEFAULT_PREFIX

    else:
        prefix = prefix[0].get("prefix")
    return commands.when_mentioned_or(prefix)(bot, message)


initial_ext = list()
bot = commands.Bot(command_prefix=get_prefix, help_command=None, case_insensitive=True)


async def create_db_pool():
    bot.db = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    print("Successfully connected to the database")
    await confirm_tables(bot.db)
    bot.cmd_cache = Tables(bot, TableType.command)
    bot.rubric_cache = Tables(bot, TableType.rubric)


@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user}")
    await bot.cmd_cache.populate()
    await bot.rubric_cache.populate()


@bot.command()
async def check(ctx):
    """
    This is used for debugging, this prints the cache into the console.
    FIXME: Remove this before merging with production branch"""

    print("cmd :")
    print(bot.cmd_cache.get_row)
    print("rubric :")
    print(bot.rubric_cache.get_row)


# To get all the .py files form the cogs folder
print("            -           ")
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        print(f"Adding {filename} from cogs...")
        initial_ext.append(f"cogs.{filename[:-3]}")


if __name__ == "__main__":
    for ext in initial_ext:
        bot.load_extension(ext)


bot.loop.run_until_complete(create_db_pool())
bot.run(os.getenv("DISCORD_TOKEN"))
