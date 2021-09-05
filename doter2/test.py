import unittest 
from domain import *

class DomainTest(unittest.TestCase):

	def test_SqlRequest(self):
		req = SqlRequest(sql_query = "SELECT * FROM abc")
		self.assertEqual(req.request().url, "https://api.opendota.com/api/explorer?sql=SELECT+%2A+FROM+abc")
		self.assertEqual(req.request().method, "GET")

	def test_sql_request(self):
		req = sql_request(3080, 3850, 7, 22, 10, limit=50000)
		self.assertEqual(req.sql_query, "SELECT match_id, avg_mmr FROM public_matches WHERE avg_mmr > 3079 AND avg_mmr < 3851 AND lobby_type = 7 AND game_mode = 22 AND start_time > extract(epoch from now()) - 864000 LIMIT 50000")
		expected_url = "https://api.opendota.com/api/explorer?sql=SELECT+match_id%2C+avg_mmr+FROM+public_matches+WHERE+avg_mmr+%3E+3079+AND+avg_mmr+%3C+3851+AND+lobby_type+%3D+7+AND+game_mode+%3D+22+AND+start_time+%3E+extract%28epoch+from+now%28%29%29+-+864000+LIMIT+50000"
		self.assertEqual(req.request().url, expected_url)

	def test_match_request(self):
		req = match_request(123456)
		self.assertEqual(req.request().url, "https://api.opendota.com/api/matches/123456")
		self.assertEqual(req.request().method, "GET")

	def test_sql_respose_from(self):
		resp = {"rowCount": 10, 
		"rows": [
			{'avg_mmr': 3080, 'match_id': 6167850708},
			{'avg_mmr': 3080, 'match_id': 6167847102},
			{'avg_mmr': 3080, 'match_id': 6167733216},
			{'avg_mmr': 3080, 'match_id': 6167734503},
			{'avg_mmr': 3080, 'match_id': 6167695513},
			{'avg_mmr': 3080, 'match_id': 6167417813},
			{'avg_mmr': 3080, 'match_id': 6167401312},
			{'avg_mmr': 3080, 'match_id': 6167368917},
			{'avg_mmr': 3080, 'match_id': 6167181016},
			{'avg_mmr': 3080, 'match_id': 6167114819}
			]
		}

		expceted = SqlResponse(rows=[SqlRow(avg_mmr=3080, match_id=6167850708), SqlRow(avg_mmr=3080, match_id=6167847102), SqlRow(avg_mmr=3080, match_id=6167733216), SqlRow(avg_mmr=3080, match_id=6167734503), SqlRow(avg_mmr=3080, match_id=6167695513), SqlRow(avg_mmr=3080, match_id=6167417813), SqlRow(avg_mmr=3080, match_id=6167401312), SqlRow(avg_mmr=3080, match_id=6167368917), SqlRow(avg_mmr=3080, match_id=6167181016), SqlRow(avg_mmr=3080, match_id=6167114819)], row_count=10)
		self.assertEqual(SqlResponse.from_resp(resp), expceted)

	def test_parse_match_request(self):
		req = parse_match_request(6167850708)
		self.assertEqual(req.request().url, "https://api.opendota.com/api/request/6167850708")
		self.assertEqual(req.request().method, "POST")
		self.assertEqual(req.request().body, None)

