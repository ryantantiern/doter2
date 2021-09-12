import attr
from typing import List, Set
from datetime import datetime

@attr.s(auto_attribs=True)
class MatchQuery:
    avg_mmr_lower: int
    avg_mmr_upper: int
    days_lag: int
    desired_num_of_results: int
    lobby_type: int
    game_mode: int

@attr.s(auto_attribs=True)
class MatchQueryResult:
    row_count: int
    rows: List['MatchQueryResultRow']
    results_received_at: datetime
    query: MatchQuery

@attr.s(auto_attribs=True)
class MatchQueryResultRow:
    match_id: int
    avg_mmr: int


@attr.s(auto_attribs=True)
class ParseMatchJob:
    job_id: int

@attr.s(auto_attribs=True)
class MatchId:
    match_id: int

@attr.s(auto_attribs=True)
class Match:
    id: int
    radiant_player_ids: Set[int]
    dire_player_ids: Set[int]
    start_time: int
    duration_seconds: int
    chats: Set['WheelChat']
    avg_mmr: int
    game_type: int
    lobby_type: int
    radiant_win: bool
    teamfights = None

@attr.s(auto_attribs=True)
class WheelChat:
    key: int
    unit: str
    time: int
    player_id: int
