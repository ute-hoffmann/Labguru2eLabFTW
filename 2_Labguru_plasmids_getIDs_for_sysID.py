import requests
import json

BASE_URL="https://my.labguru.com/api/v1"  # Use v1 for data endpoints
TOKEN="" # Labguru API token

# Headers
headers = {
    "Accept": "application/json"
}

Labguru_ID_SysID_file = "Labguru_ID_to_SysID.tsv"

# run this when executing this code for the first time
#with open(Labguru_ID_SysID_file, "w") as f:
#	f.write("Labguru_ID\tSysID\n")

# 4010 plasmids on Labguru
for page in range(42,55): # adjust range and check if pages even work
	print("current page: " + str(page))
	params={"token": TOKEN, "page":page, "page_size":100}

	r = requests.get(f"{BASE_URL}/plasmids", params=params, headers=headers)
	if r.status_code == 201 or r.status_code == 200:
		print("Everything allright")
		plasmid_list = json.loads(r.text)
		with open(Labguru_ID_SysID_file, "a") as f:
			for plasmid in plasmid_list:
				labguru_id = plasmid["id"]
				sysID = plasmid["sys_id"]
				f.write(str(labguru_id) + "\t" + str(sysID) + "\n") 
		#print(json.loads(r.text))
		#print(json.loads(r.text)[0])
		#print(json.loads(r.text)[0]["id"])
		#plasmid_id = json.loads(r.text)[0]["id"]
	else:
		print(r.status_code)

