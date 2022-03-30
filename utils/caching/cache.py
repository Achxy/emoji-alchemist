from abc import ABC, abstractmethod
from asyncpg import Pool
from collections.abc import Mapping
from pprint import pformat


class AbstractBaseCache(ABC, Mapping):
    def __init__(self, *, fetch, write, pool):
        self.fetch = fetch
        self.set = write
        self.pool = pool
        self.main_cache = {}

    @abstractmethod
    def __call__(self, bot, message) -> list[str] | None:
        ...

    def __repr__(self):
        return f"{self.__class__.__name__}({self.fetch}, {self.set})"

    def __str__(self) -> str:
        return pformat(self.main_cache)

    def __getitem__(self, __k, /):
        return self.main_cache[__k]

    def __len__(self) -> int:
        return len(self.main_cache)

    def __iter__(self):
        return iter(self.main_cache)

    def __await__(self):
        yield from self.pull().__await__()
        return self

    async def pull(self):
        response = await self.pool.fetch(self.fetch)
        journal = {}
        for val in response:
            k, v = val
            journal[k] = v
        self.main_cache = {**journal}
        del response, journal
