from typing import Dict, Tuple, List, TypeVar, Type
from datetime import datetime
import attr

from .domain import MatchQuery, MatchQueryResult, MatchQueryResultRow, Match, ChatWheel
from .adts.steps import Request, Persist, Chunk, Sequence

S = TypeVar("S")
T = TypeVar("T")


@attr.s(auto_attribs=True)
class ExplorerRequest(Request[MatchQuery, MatchQueryResult]):
    in_: Type = MatchQuery
    out_: Type = MatchQueryResult

    def project(self, response: Dict, **kwargs) -> MatchQueryResult:
        now = datetime.now()
        rows = [MatchQueryResultRow(r["match_id"], r["avg_mmr"]) for r in response["rows"]]
        return MatchQueryResult(
            row_count=response["rowCount"],
            rows=rows,
            results_received_at=now,
            query=kwargs["match_query"]
        )


@attr.s(auto_attribs=True)
class ParseMatchRequest(Request[MatchQueryResult, MatchQueryResultRow]):
    in_: Type = MatchQueryResult
    out_: Type = MatchQueryResultRow


@attr.s(auto_attribs=True)
class FetchMatchRequest(Request[MatchQueryResultRow, str]):
    in_: Type = MatchQueryResultRow
    out_: Type = str

    def project(self, response: Dict, **kwargs) -> str:
        raise NotImplemented


@attr.s(auto_attribs=True)
class NamedLocalPersist(Persist[S]):
    name: str
    out_: S = attr.ib(init=False)

    @out_.default
    def _out_default(self):
        return self.in_


@attr.s(auto_attribs=True)
class ParseAndFetchMatches(Chunk[MatchQueryResult, None]):
    in_: Type = MatchQueryResult
    out_: Type = None

    sequence = Sequence(
        in_=MatchQueryResult,
        out_=Match,
        steps=[ParseMatchRequest(), FetchMatchRequest(), NamedLocalPersist(name="matches", in_=str)]
    )

    def condition(self, state: MatchQueryResult) -> bool:
        return not self.is_empty(state)

    def update(self, arguments: Tuple[MatchQueryResult, List[Match]]) -> MatchQueryResult:
        queryResult, _ = arguments
        return attr.evolve(queryResult, row_count=queryResult.row_count - self.chunk_size, rows=queryResult.rows[1:])

    def is_empty(self, state: MatchQueryResult) -> bool:
        return state.row_count == 0


