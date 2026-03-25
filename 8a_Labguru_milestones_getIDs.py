import requests
import json

BASE_URL="https://my.labguru.com/api/v1"  # Use v1 for data endpoints
TOKEN=""  # Labguru API token

# Headers
headers = {
    "Accept": "application/json"
}


Labguru_ID_file = "Labguru_milestone_IDs.tsv"

with open(Labguru_ID_file, "w") as f:
	f.write("Labguru_ID\tTitle\tancestry\n") # \tDescription

# 4010 plasmids on Labguru
for page in range(1,40):
	print("current page: " + str(page))
	params={"token": TOKEN, "page":page, "page_size":400}

	r = requests.get(f"{BASE_URL}/milestones", params=params, headers=headers)
	if r.status_code == 201 or r.status_code == 200:
		print("Everything allright")

		project_list = json.loads(r.text)
		with open(Labguru_ID_file, "a") as f:
			for project in project_list:
				labguru_id = project["id"]
				title = project["title"]
				ancestry = project["ancestry"]
				f.write(str(labguru_id) + "\t" + str(title) + "\t" + str(ancestry) + "\n")
	else:
		print(r.status_code)

