import asyncpg
import discord
from discord.ext import commands
from tools.enum_tools import TableType
from typing import Union


__all__ = ("DatabaseTools",)


class DatabaseTools:
    def __init__(self, bot: discord.ext.commands.bot.Bot):
        self.bot = bot
        self.pool = bot.db

    async def confirm_tables(self):
        """
        The purpose of this is to create required tables if they don't exist
        This will make the bot very plug-and-play friendly
        """
        # Table for storing custom prefix
        query = """CREATE TABLE IF NOT EXISTS guilds (
                        guild_id BIGINT,
                        prefix TEXT
                        );
                    """
        await self.pool.execute(query)

        # Table for storing bot usage stats
        query = """CREATE TABLE IF NOT EXISTS usage (
                        -- We would like to have each user's usage in each channel and in each guild
                        guild_id BIGINT,
                        channel_id BIGINT,
                        user_id BIGINT,
                        type_of_cmd TEXT,
                        usage_count INT

                    );
                    """
        await self.pool.execute(query)

        # Table for storing emoji rubric stats
        query = """CREATE TABLE IF NOT EXISTS emoji_rubric(
                    guild_id BIGINT,
                    channel_id BIGINT,
                    user_id BIGINT,
                    type_of_rubric TEXT,
                    usage_count BIGINT
                    );
                """
        await self.pool.execute(query)

        # Table for storing command preferences 
        query = """CREATE TABLE IF NOT EXISTS command_preferences(
                    guild_id BIGINT,
                    ignored_command TEXT
                    );
                """
        await self.pool.execute(query)

        # Table for storing channel preferences
        query = """CREATE TABLE IF NOT EXISTS channel_preferences(
                    guild_id BIGINT,
                    channel_id BIGINT
                    );
                """
        await self.pool.execute(query)



    async def increment_usage(
        self,
        ctx,
        table: Union[TableType, str],
        value_to_increment: int = 1,
    ) -> None:
        """
        This function is used to increment the usage count of a command or emoji actions (ie, emoji rubric)
        Function name will be taken from ctx, this is what that will be logged into the database
        if the table is of instance TableType.rubric then :rubric will be appended to the end of the function name
        """

        if isinstance(table, TableType):
            table = table.value

        command_or_rubric_name = ctx.command.name

        # See if the record of user exist in database
        if table == "usage":
            column = "type_of_cmd"
        elif table == "emoji_rubric":
            column = "type_of_rubric"
            command_or_rubric_name += ":rubric"
        else:
            raise ValueError(f"Table {table} doesn't exist")

        query = f"""SELECT usage_count FROM {table}
                    WHERE (
                        guild_id = $1 AND
                        channel_id = $2 AND
                        user_id = $3 AND
                        {column} = $4
                    );
                """
        count = await self.pool.fetch(
            query, ctx.guild.id, ctx.channel.id, ctx.author.id, command_or_rubric_name
        )
        if not count:
            # Row didn't use to exist
            # Create it
            query = f"""INSERT INTO {table} (
                        guild_id,
                        channel_id,
                        user_id,
                        {column},
                        usage_count
                        )
                        VALUES (
                            $1,
                            $2,
                            $3,
                            $4,
                            $5
                        );
                    """
            await self.pool.execute(
                query,
                ctx.guild.id,
                ctx.channel.id,
                ctx.author.id,
                command_or_rubric_name,
                value_to_increment,
            )
            return

        # The row does exist
        # Which means a same user has previously used the comamnd on the same guild on the same channel
        # Increment the existing count with that of the successful additions

        # Get the integer value of usage_count from the response object
        count = int(count[0].get("usage_count"))

        # Update the existing value of usage_count to be count + successful additions
        query = """UPDATE usage
                    SET usage_count = $1
                    WHERE (
                        guild_id = $2 AND
                        channel_id = $3 AND
                        user_id = $4 AND
                        type_of_cmd = $5
                    );
                """

        await self.pool.execute(
            query,
            count + value_to_increment,
            ctx.guild.id,
            ctx.channel.id,
            ctx.author.id,
            command_or_rubric_name,
        )

    async def is_preferred_channel(self, guild_id: int, channel_id: int):
        """
        Returns true if the channel is not disabled in the guild
        else returns false
        channels can be re-enabled or disabled using the ignore / unignore command
        """
        query = """SELECT channel_id FROM channel_preferences WHERE guild_id = $1;"""
        channels = await self.pool.fetch(query, guild_id)
        if not channels:
            return True
        for channel in channels:
            if channel.get("channel_id") == channel_id:
                return False
        return True

    async def is_preferred_command(self, guild_id:int, command_name: str):
        """
        Returns true if the command is not disabled in the guild
        else returns false
        commands can be re-enabled or disabled using the enable / disable command
        """
        query = """SELECT ignored_command FROM command_preferences WHERE guild_id = $1;"""
        commands = await self.pool.fetch(query, guild_id)
        if not commands:
            return True
        for command in commands:
            if command.get("ignored_command") == command_name:
                return False
        return True
        

    async def ignore_command(self, guild_id: int, command_name: str):
        """
        This function is used to ignore a command in the guild
        """
        query = """INSERT INTO command_preferences (guild_id, ignored_command)
                    VALUES ($1, $2);"""
        await self.pool.execute(query, guild_id, command_name)


    async def unignore_command(self, guild_id: int, command_name: str):
        """
        This function is used to unignore a command in the guild
        """
        query = """DELETE FROM command_preferences WHERE guild_id = $1 AND ignored_command = $2;"""
        await self.pool.execute(query, guild_id, command_name)


    async def ignore_channel(self, guild_id: int, channel_id: int):
        """
        This function is used to ignore a channel in the guild
        """
        query = """INSERT INTO channel_preferences (guild_id, channel_id)
                    VALUES ($1, $2);"""
        await self.pool.execute(query, guild_id, channel_id)


    async def unignore_channel(self, guild_id: int, channel_id: int):
        """
        This function is used to unignore a channel in the guild
        """
        query = """DELETE FROM channel_preferences WHERE guild_id = $1 AND channel_id = $2;"""
        await self.pool.execute(query, guild_id, channel_id)
        
