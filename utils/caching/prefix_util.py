"""
EmojiWizard is a project licensed under GNU Affero General Public License.
Copyright (C) 2022-present  Achxy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

from enum import Enum
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Final,
    Generator,
    Literal,
    TypeAlias,
    TypeVar,
)

from asyncpg import Pool
from discord import Message

from .cache import BaseCache

if TYPE_CHECKING:
    from ...main import EmojiBot


_PT = TypeVar("_PT", bound="PrefixHelper")

PassIntoBase: TypeAlias = Callable[
    [list[str]], Callable[[EmojiBot, Message], list[str]]
]


class _Sentinel(Enum):
    """
    Single member enum for sentinel value
    """

    MISSING: Final = object()


class PrefixHelper(BaseCache[int, list[str]]):
    """
    A helper class for prefixes.
    This is inherited from BaseCache where the cache logic is implemented.
    """

    __slots__: tuple[str, str] = ("default", "pass_into")

    def __init__(
        self,
        *,
        fetch: str,
        write: str,
        pool: Pool,
        default: Literal[_Sentinel.MISSING] | list[str] = _Sentinel.MISSING,
        pass_into: PassIntoBase = lambda x: lambda bot, msg: x,
    ):
        """
        Constructing this class is in a similar fashion to that of `BaseCache`
        however, a new keyword argument `default` is added to specify the
        default value to be expected to the cache result.

        Args:
            fetch (str): SQL query to fetch the data from the database
            write (str): SQL query to write the data to the database
            pool (Pool): An instance of `asyncpg.Pool`
            default (list[str]): A list of default prefixes to be used
            pass_into (Callable[[list[str]], Callable[[EmojiBot, Message], list[str]]]):
                A function which takes in a list of prefixes and returns a function
                which takes in an instance of `EmojiBot` and an instance of `discord.Message`
                and returns a list of prefixes.
                This is primarily targeted for use with `commands.when_mentioned_or`
        """
        self.default: list[str] = default if default is not _Sentinel.MISSING else []
        self.pass_into: PassIntoBase = pass_into
        super().__init__(fetch=fetch, write=write, pool=pool)

    def __call__(self, bot: EmojiBot, message: Message) -> list[str]:
        """
        This can be either passed directly into `commands.Bot` constructor
        as the `command_prefix` argument or abstracted into a another helper
        function for finer control.

        Args:
            bot (EmojiBot): An instance of `EmojiBot`
            message (Message): An instance of `discord.Message`

        Returns:
            list[str]: list of strings which are cached prefixes
        """
        # NOTE: It is be better to write `self.pass_into` twice
        # than making a common base for both return case
        # this is better because the callable will get the exact
        # values that we return than some mock base
        if message.guild is None:
            return self.pass_into(self.default)(bot, message)

        ret: list[str] = self.get(message.guild.id, [])
        ret = ret if isinstance(ret, list) else [ret]

        return self.pass_into(ret + self.default)(bot, message)

    async def ensure_table_exists(self) -> None:
        """
        Calling this executes the SQL query to create the table for storing
        prefixes if it does not exist already in the database.
        """
        query: str = """
                CREATE TABLE IF NOT EXISTS prefixes (
                    guild_id bigint NOT NULL,
                    prefix text NOT NULL,
                    CONSTRAINT prefixes_pkey PRIMARY KEY (guild_id)
                );
                """
        await self.pool.execute(query)

    def __await__(self: _PT) -> Generator[Awaitable[None], None, _PT]:
        yield from self.ensure_table_exists().__await__()
        yield from self.pull().__await__()
        return self
