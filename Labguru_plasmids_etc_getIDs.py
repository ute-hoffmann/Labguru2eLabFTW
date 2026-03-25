import requests
import json

BASE_URL="https://my.labguru.com/api/v1"  # Use v1 for data endpoints
TOKEN="" # Labguru API token

# Headers
headers = {
    "Accept": "application/json"
}


Labguru_ID_file = "Labguru_plasmidsetc_IDs.tsv"

with open(Labguru_ID_file, "w") as f:
	f.write("collection\tLabguru_ID\tSysID\n") # \tDescription


collections = ["antibodies", "bacteria", "plasmids"]

for collection in collections:
	print(collection)
	if collection in ["antibodies","plasmids","bacteria"]:
		biocoll = ""
	else: 
		biocoll = "/biocollections"
	for page in range(1,40):
		print("current page: " + str(page))
		params={"token": TOKEN, "page":page, "page_size":500}
	
		r = requests.get(f"{BASE_URL}{biocoll}/{collection}", params=params, headers=headers)
		if r.status_code == 201 or r.status_code == 200:
			print("Everything allright")
	
			project_list = json.loads(r.text)
			with open(Labguru_ID_file, "a") as f:
				for project in project_list:
					labguru_id = project["id"]
					sysID = project["sys_id"]
					f.write(collection + "\t" + str(labguru_id) + "\t" + str(sysID) + "\n")
		else:
			print(r.status_code)

