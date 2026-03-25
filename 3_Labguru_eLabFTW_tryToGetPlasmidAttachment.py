import requests
import json
import elabapi_python
from client import api_client, API_KEY, API_HOST
import os

BASE_URL="https://my.labguru.com/api/v1"  # Use v1 for data endpoints
TOKEN="" # API token
headers = {
    "Accept": "application/json"
}
params={"token": TOKEN}

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
		return 1, ""

# read all IDs for eLabFTW
SysID_eLabFTW = {}
with open("../ressourcen/alreadyUploded.tsv") as plasmid_file:
	header = True
	for line in plasmid_file:
		if header: 
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		SysID_eLabFTW[split_line[0]] = split_line[3]

# read all IDs which are present on eLabFTW
Lab_SysID = {}
with open("Labguru_ID_to_SysID.tsv") as Labguru_SysID:
	header = True
	for line in Labguru_SysID:
		if header: 
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		if split_line[1] in list(SysID_eLabFTW.keys()):
			Lab_SysID[split_line[0]] = split_line[1]

plasmids_uploaded_file = "../ressourcen/plasmids_attachments_added.tsv"
#with open(plasmids_uploaded_file, "w") as f:
#	f.write("LabguruID\tSysID\teLabFTWID\n")

plasmids_uploaded_list = []
with open(plasmids_uploaded_file) as f:
	header = True
	for line in f:
		if header:
			header = False
			continue
		plasmids_uploaded_list.append(line.split("\t")[0])
	
#counter = 0
for ID in list(Lab_SysID.keys()):
	if ID in plasmids_uploaded_list:
		continue
	#counter += 1
	#if counter == 500:
	#	break
	print("Now at ID: " + str(ID))
	attachments = requests.get(f'{BASE_URL}/attachments/?&filter={{"attachable_id":"{ID}"}}', params=params, headers=headers)
	attachment_info = json.loads(attachments.text)
	item_id = SysID_eLabFTW[Lab_SysID[ID]]

	for attachment in attachment_info:
		print(attachment["id"])

		return_code, file_name = download_attachment(attachment)
		print("Return code " + str(return_code))
		print("Filename " + str(file_name))
		uploadsApi = elabapi_python.UploadsApi(api_client)
		local_file_path = file_name
		uploadsApi.post_upload('items', item_id, file=local_file_path, comment="Downloaded from Labguru")
		os.remove(local_file_path)
	with open(plasmids_uploaded_file, "a") as f:
		f.write(str(ID) + "\t" + str(Lab_SysID[ID]) + "\t" + str(item_id) + "\n")
	
