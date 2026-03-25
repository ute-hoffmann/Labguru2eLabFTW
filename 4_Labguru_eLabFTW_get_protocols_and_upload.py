# check protocol 431, 811 -> see below in code for all numbers????
# and check more thorowly for attachments - might be I skipped some....

import requests
import json
import elabapi_python
import os
from client import api_client, API_KEY, API_HOST

TOKEN="" # Labguru API token
BASE_URL="https://my.labguru.com/api/v1"

# Headers
headers = {
    "Accept": "application/json"
}


# Header for request via requests library
header_requests = {
	"Authorization": API_KEY,  # API TOKEN
	"Content-Type": "application/json",
}

params={"token": TOKEN, "page":1, "page_size":400}

def download_attachment(attachment_info):
	attach_id = attachment_info["id"]
	attachment_content_type = attachment_info["attachment_content_type"]
	attachment_headers={"Accept":attachment_content_type}
	filename = "../ressourcen/plasmid_attachments/" + attachment_info["filename"]
	params={"token": TOKEN}
	attachment_r = requests.get(f'{BASE_URL}/attachments/download?id={attach_id}', params=params, headers=attachment_headers)	
	if attachment_r.status_code == 200:
		with open(filename, "wb") as f:
			f.write(attachment_r.content)
		return 0, filename
	else:
		raise ValueError("function download_attachment: Error for attachment " + str(attach_id) + ", http status code: " + str(attachment_r.status_code))

protocols_file = "../ressourcen/protocols_uploaded.tsv"
if not os.path.isfile(protocols_file):
	with open(protocols_file, "w") as protocols_f:
		protocols_f.write("LabguruID\teLabFTW_ID\tName\tCheckAgain\n")

# read all IDs for eLabFTW
SysID_eLabFTW = {}
with open(protocols_file) as protocols_f:
	header = True
	for line in protocols_f:
		if header: 
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		SysID_eLabFTW[split_line[0]] = split_line[1]

items_client = elabapi_python.ItemsApi(api_client)

protocols = requests.get(f'{BASE_URL}/protocols', params=params)#/?token={TOKEN}&page_size=5000
print ("protocols",protocols)
protocols_list = json.loads(protocols.text)
counter = 0
for protocol in protocols_list:
	counter += 1
	excel = False
	print(str(counter) + " of " + str(len(protocols_list)))
	#if counter == 4:
	#	break
	lab_id = protocol["id"]
	print(lab_id)
	if lab_id in [431,811,831,861]:
		continue
	if str(lab_id) in list(SysID_eLabFTW.keys()):
		print(str(lab_id) + " already uploaded")
		continue

	protocol_r = requests.get(f'{BASE_URL}/protocols/{lab_id}', params={"token":TOKEN}, headers=headers)
	if not protocol_r.status_code == 200:
		raise ValueError("Error for protocol " + str(lab_id) + ", http status code: " + str(protocol_r.status_code))

	protocol_info = json.loads(protocol_r.text)
	name = protocol_info["name"]
	tags = protocol_info["tags"]
	tags.append("downloaded_from_Labguru")
	print(name)
	created_at = protocol_info["created_at"]
	updated_at = protocol_info["updated_at"]
	owner = protocol_info["owner"]["name"]
	
	procedure = ""
	local_file_paths = []
	for experiment_procedure in protocol_info["experiment_procedures"]:
		exp_proc = experiment_procedure["experiment_procedure"]
		procedure += "<h2>" + exp_proc["name"] + "</h2>"
		for part in exp_proc["elements"]:
			if part["element_type"] == "text":
				if part["data"]:
					procedure += part["data"].replace('\t', ' ').replace('\n', ' ')
			elif part["element_type"] == "attachments":
				print("check attachments for this protocol")
				excel = True
			elif part["element_type"] == "steps":
				string = part["data"].replace("\\n","").replace("\\t","").replace("<p>","").replace("</p>","").replace('<p style=\\\"\\\">','').replace('\\"','')
				#print(string)
				string = json.loads(string.replace("\\",""))
				for step in string:
					if step["title"]:
						procedure += "<p><strong>Next step:</strong>&emsp;" + step["title"] + " &emsp;"
						if step["timer"]["hours"] or step["timer"]["minutes"] or step["timer"]["seconds"]:
							procedure += "<strong>time (hh:mm:ss):</strong> " + step["timer"]["hours"] + ":" + step["timer"]["minutes"] + ":" + step["timer"]["seconds"]
						procedure += "</p>"
			elif part["element_type"] == "excel" or part["element_type"] == "samples":
				print("!!!! Check excel in this protocol !!!")
				excel = True
				continue
			elif part["element_type"] == "plate":
				print("!!! check plate in this protocol !!!")
				procedure += "<p>Check in Labguru what belongs here</p>"
				excel = True
				continue
			elif part["element_type"] == "reaction":
				print("!!! check reaction in this protocol !!!")
				procedure += "<p>Check in Labguru what belongs here</p>"
				excel = True
				continue

			else: 
				raise ValueError("found following part[element_type] " + part["element_type"] + " for " + name)
		
	eLabFTW_data = {"category": 12, "title": name, "body": procedure, "tags": tags}
	eLabFTW_metadata = {"elabftw": {"extra_fields_groups": [{"id": 1, "name": "General info"}]}, "extra_fields": {"Owner": {"type":"text", "value":owner, "group_id":1}}}
	if created_at != "null":
		eLabFTW_metadata["extra_fields"]["created_at"] = {"type":"text", "value":created_at, "group_id":1}
	if updated_at != "null":
		eLabFTW_metadata["extra_fields"]["updated_at"] = {"type":"text", "value":updated_at, "group_id":1} # ["elabftw"]
	eLabFTW_data["metadata"] = eLabFTW_metadata
	
	# upload on eLabFTW as item in correct category
	response_data, status_code, headers = items_client.post_item_with_http_info(body=eLabFTW_data)
	item_id = int(headers.get('Location').split('/').pop())
		
	if status_code == 201:
		print(f"[*] We created a Resource with ID: {item_id}")
	else:
		print(status_code)
	
	attachments = protocol_info["attachments"]
	for attachment in attachments:
		if attachment["id"] == 1107463:
			excel = True
			print("attachment " + str(attachment["id"]) + " is skipped, check this")
			continue
		return_code, file_name = download_attachment(attachment)
		if return_code:
			print("Something odd for attachment " + file_name + " in protocol " + name)
		else:
			local_file_paths.append(file_name)

	if local_file_paths:
		uploadsApi = elabapi_python.UploadsApi(api_client)
		for f in local_file_paths:
			uploadsApi.post_upload('items', item_id, file=f, comment="Downloaded from Labguru")
			os.remove(f)
			
	#if list_of_steps:
	#	for step in list_of_steps:
	#		r = requests.post(f"{API_HOST}/items/{item_id}/steps",					headers=header_requests, json={"body": step})
	#		if not r.status_code == 201:
	#			print(step)
	#			print(f"Status: {r.status_code}")

	with open(protocols_file, "a") as f:
		f.write(str(lab_id) + "\t" + str(item_id) + "\t" + name + "\t" + str(excel) + "\n")

