import requests
import json

BASE_URL="https://my.labguru.com/api/v1"  # Use v1 for data endpoints
TOKEN="" # Labguru API token

# Headers
headers = {
    "Accept": "application/json"
}


Labguru_ID_file = "Labguru_project_IDs.tsv"

with open(Labguru_ID_file, "w") as f:
	f.write("Labguru_ID\tTitle\tStart_date\tUpdated_at\tarchived\tclosed\towner\ttags\tattachments\tselectede_teams\tmilestones\texperimental_procedures\n") # \tDescription

# 4010 plasmids on Labguru
for page in range(1,201):
	print("current page: " + str(page))
	params={"token": TOKEN, "page":page, "page_size":10}

	r = requests.get(f"{BASE_URL}/projects", params=params, headers=headers)
	if r.status_code == 201 or r.status_code == 200:
		print("Everything allright")

		project_list = json.loads(r.text)
		with open(Labguru_ID_file, "a") as f:
			for project in project_list:
				archived = project["archived"]
				closed = project["closed"]
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
				f.write(str(labguru_id) + "\t" + str(title) + "\t" + str(start_date) + "\t" + str(updated_at) + "\t" + str(archived) + "\t" + str(closed)  + "\t" + str(owner) + "\t" + str(tags) + "\t" + str(attachments) + "\t" + str(selected_teams) + "\t" + str(milestones) + "\t" + str(experiment_procedures) + "\n") # + "\t" + str(description)
	else:
		print(r.status_code)

