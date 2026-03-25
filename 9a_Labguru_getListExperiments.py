import requests
import json

BASE_URL="https://my.labguru.com/api/v2"  # Use v1 for data endpoints
TOKEN="" # Labguru API token

# Headers
headers = {
    "Accept": "application/json"
}


Labguru_ID_file = "Labguru_experiment_IDs.tsv"

with open(Labguru_ID_file, "w") as f:
	f.write("Labguru_ID\tTitle\tStart_date\tUpdated_at\tflag\tsigned\twitnessed\towner\tproject\tmilestones\n")
params={"token": TOKEN}
response = requests.get(f'{BASE_URL}/experiments?&meta=true&page_size=7000&page_count=1', params=params, headers=headers)
page_count = response.json()['meta']['page_count']
print("page_count", page_count)

for page in range(1, 2):#int(page_count) +1):
	print(f"Processing  page {page}/{page_count}")
	experiments = requests.get(f'{BASE_URL}/experiments?&meta=true&page_size=7000&page_count={page}', json={"token": TOKEN})
	print ("experiments",experiments)
	experiment_list = json.loads(experiments.text)["data"]
	with open(Labguru_ID_file, "a") as f:
		for exp in experiment_list:
			labguru_id = exp["id"]
			title = exp["title"]
			start_date = exp["created_at"]
			updated_at = exp["updated_at"]
			flag = exp["flag"]
			signed = exp["signed"]
			witnessed = exp["witnessed"]
			project = exp["project"]["id"]
			milestones = exp["milestone"]
			owner = exp["owner"]["name"]
			f.write(str(labguru_id) + "\t" + str(title) + "\t" + str(start_date) + "\t" + str(updated_at) + "\t" + str(flag) + "\t" + str(signed) + "\t" + str(witnessed) + "\t" + str(owner) + "\t" + str(project) + "\t" + str(milestones) + "\n")
    
"""    
for page in range(1,201):
	print("current page: " + str(page))
	params={"token": TOKEN, "page":page, "page_size":10}

	r = requests.get(f"{BASE_URL}/experiments", params=params, headers=headers)
	if r.status_code == 201 or r.status_code == 200:
		print("Everything allright")

		project_list = json.loads(r.text)
		with open(Labguru_ID_file, "a") as f:
			for project in project_list:
				labguru_id = project["id"]
				title = project["title"]
				start_date = project["start_date"]
				updated_at = project["updated_at"]
				description = project["description"].replace('\t', ' ').replace('\n', ' ')
				owner = project["owner"]["name"]
				tags = project["tags"]
				milestones = project["milestones"]
				experiment_procedures = project["experiment_procedures"]
				attachments = project["attachments"]
				selected_teams = []
				for selected_team in project["selected_teams"]:
					selected_teams.append(selected_team["name"])
				f.write(str(labguru_id) + "\t" + str(title) + "\t" + str(start_date) + "\t" + str(updated_at) + "\t" + str(description) + "\t" + str(owner) + "\t" + str(tags) + "\t" + str(attachments) + "\t" + str(selected_teams) + "\t" + str(milestones) + "\t" + str(experiment_procedures) + "\n")
	else:
		print(r.status_code)
"""
