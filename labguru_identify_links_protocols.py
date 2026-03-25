import elabapi_python
from client import api_client, API_KEY, API_HOST
import requests
import json
import os

header_requests = {
	"Authorization": API_KEY,  # API TOKEN
	"Content-Type": "application/json",
}

def add_link_to_experiment(experiment_id, id_to_link):
	r = requests.post(f"{API_HOST}/experiments/{experiment_id}/{id_to_link}", headers=header_requests, json={"action": "create"})
	if r.status_code == 201:
		print("Link added successfully")
	else: 
		print("Link to " + id_to_link + " was not successful, return code: " + str(r.status_code))

BASE_URL="https://my.labguru.com/api/v1"  # Use v1 for data endpoints
TOKEN="" # Labguru API token
standard_headers = {
    "Accept": "application/json"
}
standard_params = {"token": TOKEN}

# we have UUIDs of experiments
# go through protocols and check which UUIDs are linked -> create these links?

# iterate through protocols
# protocol_json["links"] is a list of UUIDs
# get the correct experiment, get the correct eLabFTW number, create a link

protocols_dict = {}
protocols_file = "../ressourcen/protocols_uploaded.tsv"
with open(protocols_file) as f:
	header = True
	for line in f: 
		if header:
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		protocols_dict[split_line[0]] = split_line[1]

Labguru_eLabFTW_dict = {}
with open("LabguruID_eLabFTWID_all.tsv") as f:
	for line in f:
		split_line = line.strip("\n").split("\t")
		if split_line[0] not in Labguru_eLabFTW_dict.keys():
			Labguru_eLabFTW_dict[split_line[0]] = {split_line[1]:split_line[2]}
		else:
			Labguru_eLabFTW_dict[split_line[0]][split_line[1]] = split_line[2]
# use this below to link eLabFTW -> Labguru		

UUID_experiments_eLabFTW_dict = {}
with open("../ressourcen/experiments_downloaded.tsv") as f:
	header = True
	for line in f: 
		if header:
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		try:
			UUID_experiments_eLabFTW_dict[split_line[5]] = Labguru_eLabFTW_dict["experiments"][split_line[0]]
		except KeyError:
			continue

	
		
for LabguruID in list(protocols_dict.keys()):
	# download protocols json
	if LabguruID in [431,811,831,861]:
		continue
	
	protocol_r = requests.get(f'{BASE_URL}/protocols/{LabguruID}', params={"token":TOKEN}, headers=standard_headers)
	if not protocol_r.status_code == 200:
		raise ValueError("Error for protocol " + str(LabguruID) + ", http status code: " + str(protocol_r.status_code))

	protocol_info = json.loads(protocol_r.text)
	
	eLabFTW_ID_protocol = Labguru_eLabFTW_dict["protocols"][LabguruID]
	
	links = protocol_info["links"]
	for link in links:
		if link in list(UUID_experiments_eLabFTW_dict.keys()):
			add_link_to_experiment(UUID_experiments_eLabFTW_dict[link], "items_links/" + str(eLabFTW_ID_protocol))
			print("Linked eLabFTW experiment ID " + UUID_experiments_eLabFTW_dict[link] + " to protocol " + str(eLabFTW_ID_protocol))
