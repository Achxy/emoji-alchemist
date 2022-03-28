from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Concatenate,
    ParamSpec,
    TypeAlias,
    TypeVar,
)

if TYPE_CHECKING:
    from caching_pods import CachingPod

CoroFunc: TypeAlias = Callable[..., Awaitable[Any]]

CPT = TypeVar("CPT", bound="CachingPod")
CFT = TypeVar("CFT", bound=CoroFunc)
P = ParamSpec("P")
R = TypeVar("R")

AsyncDestination: TypeAlias = dict[str, list[CoroFunc]]
AsyncOuterDecoratorHint: TypeAlias = Callable[
    [Callable[Concatenate[CPT, P], Awaitable[R]]],
    Callable[Concatenate[CPT, P], Awaitable[R]],
]
SyncOuterDecoratorHint: TypeAlias = Callable[
    [Callable[Concatenate[CPT, P], R]],
    Callable[Concatenate[CPT, P], R],
]
