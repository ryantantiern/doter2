import json
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, List, TypeVar

import attr
from requests import Request as RRequest, Response, Session

from doter2.domain import MatchQuery, MatchQueryResult, MatchQueryResultRow, ParseMatchJob, Match
from doter2.steps import ExplorerRequest, ParseMatchRequest, FetchMatchRequest, NamedLocalPersist
from doter2.adts.interpreter import StepInterpreter, WorkflowInterpreter
from doter2.adts.steps import Request, Persist

S = TypeVar("S")
T = TypeVar("T")

SENT_REQUESTS = []
SESSION = Session()
SESSION.headers.update({"Connection": "keep-alive", "Accept-Encoding": "gzip, deflate, br", "Accept": "*/*", "User-Agent": "PostmanRuntime/7.28.4"})


def validate_is_dir(p: Path):
    if not p.is_dir():
        raise ValueError("Expected directory, found " + str(p))


@attr.s(auto_attribs=True, frozen=True)
class LocalWorkflowInterpreter(WorkflowInterpreter[MatchQuery, None]):
    save_to: Path

    def __attrs_post_init__(self):
        validate_is_dir(self.save_to)

    def request_interpreter(self, req: Request[S, T]) -> StepInterpreter[Request[S, T]]:
        if isinstance(req, ExplorerRequest):
            return ExplorerRequestInterpreter(req)
        elif isinstance(req, ParseMatchRequest):
            return ParseMatchRequestInterpreter(req)
        elif isinstance(req, FetchMatchRequest):
            return FetchMatchRequestInterpreter(req)
        else:
            raise ValueError("Step not supported: " + str(str))

    def persist_interpreter(self, pers: Persist[S]) -> StepInterpreter[Persist[S]]:
        return LocalPersistInterpreter(step=pers, dir=self.save_to)


@attr.s(auto_attribs=True, frozen=True)
class OpenDotaRequestInterpreter(StepInterpreter):
    base_url = "https://api.opendota.com/api"
    sent_requests = SENT_REQUESTS
    s = SESSION

    def send(self, req: RRequest) -> Response:
        # When we hit more than 50 request logs, remove all request logs
        # that are older than 1 minute from now
        while len(self.sent_requests) > 50:
            while len(self.sent_requests) > 0 and datetime.now().timestamp() - self.sent_requests[0] > 60:
                del self.sent_requests[0]

            if len(self.sent_requests) > 50:
                # We are making requests to quickly. Let's just wait a whole minute
                # so that we can clear the entire request log
                time.sleep(60)

        print(f"Sending request -- {req.method} {req.url}")
        now = datetime.now().timestamp()
        self.sent_requests.append(now)
        return self.s.send(req.prepare())

    def url_from(self, url: str, path_params: List[str] = []) -> str:
        if url[0] != "/":
            url = f"/{url}"
        return self.base_url + url.format(*path_params)


@attr.s(auto_attribs=True, frozen=True)
class ExplorerRequestInterpreter(OpenDotaRequestInterpreter):
    step: ExplorerRequest
    method = "get"
    url = "/explorer"

    def build_callable(self) -> Callable[[MatchQuery], MatchQueryResult]:
        def f(s: MatchQuery) -> MatchQueryResult:
            secs_lag = s.days_lag * 86400
            sql = f"SELECT match_id, avg_mmr FROM public_matches WHERE avg_mmr > {s.avg_mmr_lower - 1} AND " \
                  f"avg_mmr < {s.avg_mmr_upper + 1} AND lobby_type = {s.lobby_type} AND game_mode = {s.game_mode} " \
                  f"AND start_time > extract(epoch from now()) - {secs_lag} LIMIT {s.desired_num_of_results}"
            req = RRequest(method=self.method, url=self.url_from(self.url), params=[("sql", sql)])
            data = self.send(req).json()
            return self.step.project(data, match_query=s)

        return f


@attr.s(auto_attribs=True, frozen=True)
class ParseMatchRequestInterpreter(OpenDotaRequestInterpreter):
    method = "post"
    url = "/request/{}"

    def build_callable(self) -> Callable[[MatchQueryResult], MatchQueryResultRow]:
        def request_parse_match(mqrr: MatchQueryResultRow) -> ParseMatchJob:
            req = RRequest(method=self.method, url=self.url_from(self.url, [str(mqrr.match_id)]))
            data = self.send(req).json()
            return ParseMatchJob(data["job"]["jobId"])

        def ensure_match_is_parsed(job: ParseMatchJob) -> None:
            req = RRequest(method="get", url=self.url_from(self.url, [str(job.job_id)]))
            data = {}
            retry = 6
            sleep_time = 16
            time.sleep(sleep_time)
            while retry > 0:
                data = self.send(req).json()
                if data is None:
                    break
                sleep_time = int(sleep_time * 0.7)
                time.sleep(sleep_time)
                retry -= 1

            if retry == 0 and data is not None:
                raise Exception("Failed to parse match -- {}".format(json.dumps(data)))


        def f(s: MatchQueryResult) -> MatchQueryResultRow:
            parse_job_id = request_parse_match(s.rows[0])
            ensure_match_is_parsed(parse_job_id)
            return s.rows[0]

        return f


@attr.s(auto_attribs=True, frozen=True)
class FetchMatchRequestInterpreter(OpenDotaRequestInterpreter):
    step: FetchMatchRequest
    method = "get"
    url = "/matches/{}"

    def build_callable(self) -> Callable[[MatchQueryResultRow], str]:
        def f(s: MatchQueryResultRow) -> Match:
            req = RRequest(method=self.method, url=self.url_from(self.url, [str(s.match_id)]))
            # data = self.send(req).json()
            data = self.send(req).text
            return data

        return f


@attr.s(auto_attribs=True, frozen=True)
class LocalPersistInterpreter(StepInterpreter[NamedLocalPersist[S]]):
    step: NamedLocalPersist[S]
    dir: Path

    def build_callable(self) -> Callable[[S], S]:
        def f(s: S) -> S:
            separators = (',', ':')
            if attr.has(s):
                json_line = json.dumps(attr.asdict(s), separators=separators)
            else:
                json_line = s
            json_line = json_line + "\n"
            file = self.dir / Path(self.step.name)
            with open(file, "a") as fp:
                print("writing to " + str(file))
                fp.write(json_line)
            return s

        return f
