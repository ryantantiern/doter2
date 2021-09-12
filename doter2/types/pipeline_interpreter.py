import attr
from abc import abstractmethod
from typing import Callable, TypeVar, Union
from .base_pipeline import Request, Persist

S = TypeVar("S")
T = TypeVar("T")
R = TypeVar("T")

@attr.s
class PipelineInterpreter:

    @abstractmethod
    def interpret_request(self, req: Request[R, S, T]) -> Callable[[S], Union[Exception, T]]:
        raise NotImplementedError

    @abstractmethod
    def interpret_persist(self, pers: Persist[S, S]) -> Callable[[S], Union[Exception, S]]:
        raise NotImplementedError

    @abstractmethod
    def interpret_seqeuence(self, seq: ):

