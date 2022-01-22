import discord
import typing
from discord.ext import commands


class add_(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO: Add more features and error handling to this.
    # TODO: Check for guild vacancy for additonal emotes
    @commands.command()
    @commands.has_permissions(manage_emojis=True)
    async def add(self, ctx, *emojis: typing.Union[discord.PartialEmoji, str]):
        for index, each_emoji in enumerate(emojis):

            if isinstance(each_emoji, str):
                # To not process anything further if the user has given us an non-custom emoji.
                embed = discord.Embed(
                    title="That is not a custom emote",
                    description=f"{each_emoji} is not an custom emote and thus cannot be added to your guild",
                )
                embed.set_footer(
                    text=f"{index + 1} of {len(emojis)} to add {'' if not (index + 1) == len(emojis) else '(over)'}"
                )
                await ctx.send(embed=embed)
                continue

            # All working, add the emoji to the guild.
            added_emoji = await ctx.guild.create_custom_emoji(
                name=each_emoji.name,
                image=await each_emoji.read(),
                reason=f"This emoji was added by {ctx.author} ({ctx.author.id})",
            )
            # Display the success message.
            embed = discord.Embed(
                title=f"Successfully added {added_emoji.name}",
                description=f"Successfully added {added_emoji} to the guild.",
            )
            embed.set_footer(
                text=f"{index + 1} of {len(emojis)} to add {'' if not (index + 1) == len(emojis) else '(over)'}"
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(add_(bot))
