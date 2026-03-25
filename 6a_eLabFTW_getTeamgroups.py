# needs correct mamba environment; before running script run:  
# mamba activate API 

import elabapi_python
from client import api_client, API_KEY, API_HOST
import json
import requests

# Header for request via requests library
header_requests = {
	"Authorization": API_KEY,  # API TOKEN
	"Content-Type": "application/json",
}
# Payload for the  POST request (to adapt)
payload_requests = {
	"qty_stored": "1",
	"qty_unit": "tube"
}


r = requests.get(f"{API_HOST}/teams/4/teamgroups",headers=header_requests)
print(r.status_code)
print(r.text)
