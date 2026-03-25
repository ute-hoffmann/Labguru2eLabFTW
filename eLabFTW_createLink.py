import requests
import elabapi_python
from client import api_client, API_KEY, API_HOST
import ast
import os
import json

# Header for request via requests library
header_requests = {
	"Authorization": API_KEY,  # API TOKEN
	"Content-Type": "application/json",
	'accept': '*/*'
}

def add_link_to_experiment(experiment_id, id_to_link):
	# add links to experiments
	# API end point: POST /{entity_type}/{id}/experiments_links/{subid}
	# example value: {"action":"create"}
	# Response: 201
	r = requests.post(f"{API_HOST}/experiments/{experiment_id}/items_links/{id_to_link}", headers=header_requests, json={"action": "create"})
	if r.status_code == 201:
		print("Link added successfully")
	else: 
		print("Link to " + id_to_link + " was not successful, return code: " + str(r.status_code))
		
add_link_to_experiment("5950", "9615")
