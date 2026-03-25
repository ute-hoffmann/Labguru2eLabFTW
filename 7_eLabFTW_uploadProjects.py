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
}

canwrite = { 'base': 20, 'teams': [], 'teamgroups': [8], 'users': [] }

experimentsApi = elabapi_python.ExperimentsApi(api_client)
uploadsApi = elabapi_python.UploadsApi(api_client)

def create_experiment_page(exp_data):
	# For this we need an "experiments" endpoint client object
	exp_client = elabapi_python.ExperimentsApi(api_client)

	response_data, status_code, headers = exp_client.post_experiment_with_http_info(body=exp_data)
	location = headers.get('Location')
	exp_id = int(location.split('/').pop())
	# A status code of 201 means the entry was created
	if status_code == 201:
		print(f"[*] We created an experiment. The status code is {status_code} and the experiment is at: {exp_id}")
		return exp_id
	

def upload_file_to_experiment(experiment_ID, file_name):
	uploadsApi.post_upload('experiments', experiment_ID, file=file_name, comment='Transferred from Labguru')


def add_comment_to_experiment(experiment_id, experiment_comment):
	# add comments
	# API end point: POST /{entity_type}/{id}/comments # entity_type = experiments, items
	# example value: {"comment": "string"}
	# Response: 201
	r = requests.post(f"{API_HOST}/experiments/{experiment_id}/comments", headers=header_requests, json={"comment": experiment_comment})
	if r.status_code == 201:
		print("Comment uploaded successfully")

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
		
if __name__ == "__main__":
	uploaded_file = "../ressourcen/eLabFTW_projects_uploaded.tsv"
	projects_uploaded = {}
	if not os.path.isfile(uploaded_file):
		with open(uploaded_file, "w") as f:
			f.write("LabguruID\teLabFTW_ID\n")
	else:
		with open(uploaded_file) as f:
			header = True
			for line in f:
				if header: 
					header = False
					continue
				projects_uploaded[line.split("\t")[0]] = line.strip("\n").split("\t")[1]


	projects_file = "../ressourcen/projects_downloaded.tsv"
	projects_downloaded = {}
	counter = 0
	with open(projects_file) as f:
		header = True
		for line in f:
			counter += 1
			#if counter == 2:
			#	break
			if header:
				header = False
				continue
			split_line = line.strip("\n").split("\t")
			json_name = "../ressourcen/project_jsons/" + split_line[2]
			if split_line[0] in list(projects_uploaded.keys()):
				print("Project with ID " + str(split_line[0]) + " was already uploaded under eLabFTW ID " + str(projects_uploaded[split_line[0]]))
				continue
			json_data = ""
			with open(json_name) as f:
				json_data = ast.literal_eval(f.read())
				
			if json_data:
				item_id = create_experiment_page(json_data)
			else:
				print("No json? skip this project: " + split_line[0])

			eLabFTW_links = ast.literal_eval(split_line[3])				
			for eLabFTW_ID in eLabFTW_links:
				add_link_to_experiment(item_id, eLabFTW_ID)

			attachments = ast.literal_eval(split_line[4])
			for attachment in attachments:
				print(attachment)
				upload_file_to_experiment(item_id, attachment)
			
			comments = ast.literal_eval(split_line[5])
			for comment in comments:
				add_comment_to_experiment(item_id, comment)
				
			# change can edit to seniorlabmembers
			experimentsApi.patch_experiment(item_id, body={'canwrite': json.dumps(canwrite)})
			
			with open(uploaded_file, "a") as f:
				f.write(str(split_line[0]) + "\t" + str(item_id) + "\n")
			with open("LabguruID_eLabFTWID_all.tsv", "a") as f:
				f.write("project\t" + split_line[0] + "\t" + str(item_id) + "\n")
