# import attr
# from requests import PreparedRequest, Request
# from abc import abstractmethod
# from typing import Optional, Dict, List
#
# OPEN_DOTA_BASE_URL = "https://api.opendota.com/api"
#
# GET_METHOD = "get"
# POST_METHOD = "post"
#
# def url_from(base, url, path_params: List[str] = []) -> str:
# 	if url[0] != "/":
# 		url = f"/{url}"
# 	return base + url.format(*path_params)
#
# @attr.s(auto_attribs=True)
# class OpenDotaRequest(object):
# 	method: str
# 	url: str
# 	base_url: str = attr.ib(init=False)
#
# 	def __attrs_post_init__(self):
# 		self.base_url = OPEN_DOTA_BASE_URL
#
# 	@abstractmethod
# 	def request(self) -> PreparedRequest:
# 		raise NotImplementedError()
#
# @attr.s(auto_attribs=True)
# class GetOpenDotaRequest(OpenDotaRequest):
# 	path_params: List[str] = attr.ib(init=False)
# 	query_params: Dict[str, str] = attr.ib(init=False)
# 	method: str = attr.ib(init=False)
#
# 	def __attrs_post_init__(self):
# 		super().__attrs_post_init__()
# 		self.method = GET_METHOD
#
# @attr.s(auto_attribs=True)
# class PostOpenDotaRequest(OpenDotaRequest):
# 	path_params: List[str] = attr.ib(init=False)
# 	query_params: Dict[str, str] = attr.ib(init=False)
# 	body: Dict = attr.ib(init=False)
# 	method: str = attr.ib(init=False)
#
# 	def __attrs_post_init__(self):
# 		super().__attrs_post_init__()
# 		self.method = POST_METHOD
#
#
# @attr.s(auto_attribs=True)
# class SqlRequest(GetOpenDotaRequest):
# 	sql_query: str
# 	method: str = attr.ib(init=False)
# 	url: str = "/explorer"
#
# 	def __attrs_post_init__(self):
# 		super().__attrs_post_init__()
# 		self.query_params = { "sql": self.sql_query }
# 		self.path_params = []
#
# 	def request(self) -> PreparedRequest:
# 		return Request(method=self.method, url=url_from(self.base_url, self.url), params=self.query_params).prepare()
#
# @attr.s(auto_attribs=True)
# class SqlResponse:
# 	rows: List['SqlRow']
# 	row_count: int
#
# 	@staticmethod
# 	def from_resp(data) -> List['SqlRow']:
# 		row_data = list(map(lambda a: SqlRow(a["avg_mmr"], a["match_id"]), data["rows"]))
# 		return SqlResponse(row_count = data["rowCount"], rows = row_data)
#
#
# @attr.s(auto_attribs=True)
# class SqlRow:
# 	avg_mmr: str
# 	match_id: str
#
# @attr.s(auto_attribs=True)
# class ParseMatchRequest(PostOpenDotaRequest):
# 	match_id: int
# 	url: str = "/request/{}"
# 	query_params: Dict[str, str] = attr.ib(factory=dict)
#
# 	def __attrs_post_init__(self):
# 		super().__attrs_post_init__()
# 		self.path_params = [self.match_id]
# 		self.body = {}
#
# 	def request(self) -> PreparedRequest:
# 		return Request(method=self.method, url=url_from(self.base_url, self.url, self.path_params)).prepare()
#
# @attr.s(auto_attribs=True)
# class MatchRequest(OpenDotaRequest):
# 	match_id: int
# 	method: str = GET_METHOD
# 	url: str = "/matches/{}"
#
# 	def request(self) -> PreparedRequest:
# 		return Request(method=self.method, url=url_from(self.base_url, self.url, [self.match_id])).prepare()
#
#
#
# @attr.s(auto_attribs=True)
# class MatchRow:
# 	chats: List['Chat']
#
# class Chat:
# 	pass
#
#
# def match_request(match_id: int) -> MatchRequest:
# 	return MatchRequest(match_id)
#
# def sql_request(avg_mmr_lower: int, avg_mmr_upper: int, lobby_type: int, game_mode: int, day_lag: int, limit: int = 50000) -> SqlRequest:
# 	secs_lag = day_lag * 86400
# 	sql = f"SELECT match_id, avg_mmr FROM public_matches WHERE avg_mmr > {avg_mmr_lower-1} AND avg_mmr < {avg_mmr_upper+1} AND lobby_type = {lobby_type} AND game_mode = {game_mode} AND start_time > extract(epoch from now()) - {secs_lag} LIMIT {limit}"
# 	return SqlRequest(sql_query=sql)
#
# def parse_match_request(match_id: int) -> ParseMatchRequest:
# 	return ParseMatchRequest(match_id)
#
#
