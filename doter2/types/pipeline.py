from typing import Dict, Tuple

from .base_pipeline import *
from .domain import *

R = TypeVar("R")

@attr.s(auto_attribs=True)
class ExplorerRequest(Request[Dict, MatchQuery, MatchQueryResult]):
    projection: Callable[Dict, MatchQueryResult]

    def projection(self, response: Dict) -> MatchQueryResult:
        pass

@attr.s(auto_attribs=True)
class ParseMatchRequest(Request[Dict, MatchQueryResultRow, MatchId]):
    def projection(self, response: Dict) -> MatchQueryResultRow:
        pass

@attr.s(auto_attribs=True)
class FetchMatch(Request[Dict, MatchId, Match]):
    def projection(self, response: Dict) -> Match:
        pass

@attr.s(auto_attribs=True)
class ParseAndFetchMatches(Chunk[MatchQueryResult, List[Match]]):
    def __attrs_post_init__(self):
        self.sequence = Sequence(
            steps = [ParseMatchRequest(), Persist(), FetchMatch(), Persist()]
        )

    def condition(self, state: MatchQueryResult) -> bool:
        return self.is_empty(state)

    def update(self, arguments: Tuple[MatchQueryResult, List[Match]]) -> MatchQueryResult:
        queryResult, _ = arguments
        return attr.evolve(queryResult, row_count = queryResult.row_count - self.chunk_size)

    def is_empty(self, state: MatchQueryResult) -> bool:
        return state.row_count == 0