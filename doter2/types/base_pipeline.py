import attr
from abc import abstractmethod
from typing import List, Generic, TypeVar, Callable, Any, Optional

S = TypeVar("S")
T = TypeVar("T")
R = TypeVar("R")

@attr.s(auto_attribs=True)
class Step(Generic[S, T]):
    """A computational where input is S and output is T"""
    pass

@attr.s(auto_attribs=True)
class Sequence(Step[S, T]):
    """A sequence of Steps where input of first Step is S and
       output of last Step is T"""
    steps: List[Step]

@attr.s(auto_attribs=True)
class Loop(Step[S, T]):
    """Continuously runs the Sequence with input `state` while the `condition` is met. After each Sequence, `update`
    updates the `state` then the loop is invoked again with the new state."""

    sequence: Sequence[S, T] = attr.ib(init=False)

    @abstractmethod
    def condition(self, state: S) -> bool:
        raise NotImplementedError

    @abstractmethod
    def update(self, arguments: (S, T)) -> S:
        raise NotImplementedError

@attr.s(auto_attribs=True)
class Persist(Step[S, S]):
    """A computation that persists S"""
    pass

@attr.s(auto_attribs=True)
class Request(R, Step[S, T]):
    """Represents a request to perform some computation that expects a response R. R projected as the expected output
       T using `projection`"""
    @abstractmethod
    def projection(self, response: R) -> T:
        raise NotImplementedError

@attr.s(auto_attribs=True)
class Chunk(Loop[S, T]):
    """A Loop that breaks when the state is `empty`"""
    chunk_size: int

    @abstractmethod
    def is_empty(self, state: S) -> bool:
        raise NotImplementedError

