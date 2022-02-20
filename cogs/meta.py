import disnake as discord
from disnake.ext import commands


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """
        Sends an embed with the bot's latency
        but really this command is just used to test the bot's responsiveness
        """
        embed = discord.Embed(
            title="Pong! 🏓",
            description=f"Current Latency of the bot is {round(self.bot.latency * 1000)}ms",
        )
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, new_prefix: str):
        """
        Changes the bot's prefix for specific guilds
        """
        await self.bot.tools.set_prefix(ctx.guild.id, new_prefix)

        embed = discord.Embed(
            title="Successfully changed prefix",
            description=f"The old prefix used to be **{ctx.prefix}** now its **{new_prefix}**",
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Meta(bot))
