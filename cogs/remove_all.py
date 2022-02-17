import disnake as discord
from disnake.ext import commands
from tools.enum_tools import TableType
from helpers.context_patch import EditInvokeContext, PatchedContext


class RemoveAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def remove_all(self, ctx: EditInvokeContext | PatchedContext):
        """
        Takes no parameters, removes all emojis from the server
        """

        count: int = 0
        for each_emoji in ctx.guild.emojis:
            count += 1
            try:
                await each_emoji.delete()
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass
            else:
                embed = discord.Embed(
                    title="Success!",
                    description=f"Removed **{each_emoji}** from the server",
                )
                embed.set_footer(text=f"{len(ctx.guild.emojis)} more to go")
                await ctx.send(embed=embed)

        await self.bot.tools.increment_usage(
            ctx,
            TableType.rubric,
            count,
        )


def setup(bot):
    bot.add_cog(RemoveAll(bot))
