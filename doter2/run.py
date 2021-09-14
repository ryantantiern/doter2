from pathlib import Path

from doter2.interpreter import LocalWorkflowInterpreter
from doter2.steps import *
from doter2.adts.steps import Step

DATA_DIR = Path("C:\\workspace\\doter2\\data")


def output_type(step: Step): return step.out_
def input_type(step: Step): return step.in_

def create_workflow(chunk_size: int) -> Sequence:
    return Sequence(
        in_=None,
        out_=None,
        steps=[ExplorerRequest(), ParseAndFetchMatches(chunk_size)]
    )


def run():
    fetch_matches_query = MatchQuery(avg_mmr_lower=3450,
                   avg_mmr_upper=3850,
                   lobby_type=7,
                   game_mode=22,
                   days_lag=10,
                   desired_num_of_results=20)
    workflow = create_workflow(1)
    local_interpreter = LocalWorkflowInterpreter(save_to=DATA_DIR, run=None).build(workflow)
    local_interpreter.run(fetch_matches_query)

if __name__ == "__main__":
    run()