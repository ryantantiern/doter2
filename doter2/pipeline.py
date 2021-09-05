from domain import SqlRequest, sql_request, match_request, SqlResponse
from requests import Session
from pprint import pprint
import attr

matches_queue = []
parse_jobs = []
parse_jobs_map = {} # job_id -> match_id


s = Session()

sql_req = sql_request(avg_mmr_lower = 3080, avg_mmr_upper = 3850, lobby_type = 7, game_mode = 22, day_lag = 10, limit=2).request()
print("Sending sql request")
sql_resp = s.send(sql_req)
data = sql_resp.json()
sql_resp = SqlResponse.from_resp(data)
matches_queue = matches_queue + [a.match_id for a in sql_resp.rows]
print("Buiding queue: " + str(matches_queue))

while matches_queue:	
	match_id = matches_queue[0]
	req = match_request(match_id).request()
	resp = s.send(req)
	data = resp.json()
	pprint(data)
	matches_queue = matches_queue[1:]











