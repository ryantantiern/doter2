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
class FetchMatchRequest(Request[MatchQueryResultRow, Match]):
    in_: Type = MatchQueryResultRow
    out_: Type = Match

    def project(self, response: Dict, **kwargs) -> Match:
        def deserialize_chatwheel(d: Dict) -> ChatWheel:
            return ChatWheel(key=int(d["key"]), slot=d["slot"], time=d["time"], player_id=d["player_slot"])

        chat = response["chat"]
        chat_wheels = [deserialize_chatwheel(c) for c in chat if c["type"] == "chatwheel"]
        players = response["players"]
        radiant_players = [p["player_slot"] for p in players if p["player_slot"] <= 127]
        dire_players = [p["player_slot"] for p in players if p["player_slot"] >= 128]
        return Match(
            id=response["match_id"],
            radiant_player_slots=radiant_players,
            dire_player_slots=dire_players,
            start_time=response["start_time"],
            duration_seconds=response["duration"],
            chats=chat_wheels,
            avg_mmr=kwargs["row"].avg_mmr,
            game_mode=response["game_mode"],
            lobby_type=response["lobby_type"],
            radiant_win=response["radiant_win"]
        )


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
        steps=[ParseMatchRequest(), FetchMatchRequest(), NamedLocalPersist(name="matches", in_=Match)]
    )

    def condition(self, state: MatchQueryResult) -> bool:
        return not self.is_empty(state)

    def update(self, arguments: Tuple[MatchQueryResult, List[Match]]) -> MatchQueryResult:
        queryResult, _ = arguments
        return attr.evolve(queryResult, row_count=queryResult.row_count - self.chunk_size, rows=queryResult.rows[1:])

    def is_empty(self, state: MatchQueryResult) -> bool:
        return state.row_count == 0


