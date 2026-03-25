import requests
import json

BASE_URL="https://my.labguru.com/api/v1"  # Use v1 for data endpoints
TOKEN="" # Labguru API token

# Headers
headers = {
    "Accept": "application/json"
}

params={"token": TOKEN}

ids = [11, 21, 31, 1008111, 1008504, 1008505, 1008506, 1008507]

with open("Labguru_exampleMilestones.txt", "w") as f:
	for i in ids:
		r = requests.get(f"{BASE_URL}/milestones/{i}", params=params, headers=headers)

		f.write("milestone " + str(i))
		f.write(str(r.status_code))
		f.write(r.text)
