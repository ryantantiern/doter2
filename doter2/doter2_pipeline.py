from types.pipeline import *


def doter2_pipeline(chunk_size: int) -> Sequence:
    return Sequence(
        steps = [ExplorerRequest(), ParseAndFetchMatches(chunk_size), Persist()]
    )

fetch_matches_query = [
    MatchQuery(avg_mmr_lower = 3080,
               avg_mmr_upper = 3850,
               lobby_type = 7,
               game_mode = 22,
               days_lag = 10,
               desired_num_of_results=2)
]





