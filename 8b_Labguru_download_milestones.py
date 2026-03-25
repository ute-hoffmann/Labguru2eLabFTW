import elabapi_python
from client import api_client, API_KEY, API_HOST
import requests
import json
import os

list_of_all_attachments = []

BASE_URL="https://my.labguru.com/api/v1"  # Use v1 for data endpoints
TOKEN="" # Labguru API token
standard_headers = {
    "Accept": "application/json"
}
standard_params = {"token": TOKEN}

Labguru_eLabFTW_dict = {}
with open("LabguruID_eLabFTWID_all.tsv") as f:
	header = True
	for line in f:
		if header:
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		if split_line[0] not in Labguru_eLabFTW_dict.keys():
			Labguru_eLabFTW_dict[split_line[0]] = {split_line[1]: split_line[2]}
		else:
			Labguru_eLabFTW_dict[split_line[0]][split_line[1]] = split_line[2]
			

# to be tested, better connection with attachments etc.
def download_elements_experiment_procedures(element_id):
	element_r = requests.get(f'{BASE_URL}/elements/{element_id}', params=standard_params, headers=standard_headers)
	if not element_r.status_code == 200:
		raise ValueError("function download_elements_experiment_procedures: Error for experiment " + str(element_id) + ", http status code: " + str(element_r.status_code))
		return 1

	write_text = ""
	
	element_json = json.loads(element_r.text)
	element_type = element_json["element_type"]
	
	attachments_list_of_files = []
	samples_to_be_linked = []
	excel_alert = False
	
	if not element_json["data"]:
		return write_text, excel_alert, attachments_list_of_files, samples_to_be_linked
	
	if element_type == "text":
		write_text += element_json["data"]
	elif element_type == "attachments":
		write_text += "" # most likely already exists as attachment
	elif element_type == "excel":
		write_text += "<h2>Excel linked here</h2><p>Check Labguru to see this...</p>"
		excel_alert = True
	elif element_type == "samples":
		write_text += "<h2>Samples and Reagents</h2>"
		string = json.loads(element_json["data"].replace('\\','')) # part to element_json
		for item in string["samples"]:
			lab_id = item["item"]["item_id"]
			url = item["url"]
			name_item = item["name"]
			samples_to_be_linked.append(url)
			write_text += name_item + " (Labguru URL: " + str(url) + ") was used, link to eLabFTW ID will be linked below, if possible<br>"

	
	return write_text, excel_alert, attachments_list_of_files, samples_to_be_linked

# this function worked in a different file already :) 
def download_attachment(attachment_info):
	attach_id = attachment_info["id"]
	attachment_content_type = attachment_info["attachment_content_type"]
	attachment_headers={"Accept":attachment_content_type}
	attach_filename = attachment_info["filename"]
	if " " in attach_filename:
		split_attach_filename = attach_filename.split(" ")
		attach_filename = ""
		for part in split_attach_filename: 
			attach_filename += part + "_"
		attach_filename = attach_filename[:-1]
	filename = "../ressourcen/project_attachments/" + attach_filename
	if filename in list_of_all_attachments:
		print("Attention ! filename " + filename + " has filename which already occurred! appending 'another_' to beginning")
		filename = "../ressourcen/project_attachments/another_" + attach_filename
	list_of_all_attachments.append(filename)
	attachment_r = requests.get(f'{BASE_URL}/attachments/download?id={attach_id}', params=standard_params, headers=attachment_headers)
	
	if attachment_r.status_code == 200:
		with open(filename, "wb") as f:
			f.write(attachment_r.content)
		return 0, filename
	else:
		raise ValueError("function download_attachment: Error for attachment " + str(attach_id) + ", http status code: " + str(attachment_r.status_code))
		return 1, ""

# go through everything again: all relevant fields there? or some missing?
def download_milestone(project_number):
	r = requests.get(f"{BASE_URL}/milestones/{project_number}", params=standard_params, headers=standard_headers)
	if not r.status_code == 200:
		raise ValueError("function download_project: Error for project " + project_number + ", http status code: " + str(r.status_code))
		return 1
		
	project_info = json.loads(r.text)

	labguru_id = project_info["id"]
	title = "Subfolder: " + project_info["title"]
	project_belongs_to = project_info["project_id"] # link this
	
	created_at = project_info["created_at"] # null if not present
	updated_at = project_info["updated_at"]
	ancestry = project_info["ancestry"] # link this
	# run once with these three lines uncommented, then run again with commenting them
	#if not ancestry == None:
	#	print("Ancestry - skipping and run after upload to eLabFTW!")
	#	return 1, 2,3,4,5,6

	owner = project_info["owner"]["name"]
	tags = project_info["tags"]
	tags.append("Download-Labguru")
	tags.append(owner)
	
	comments = project_info["comments"]

	# iterate attachments
	attachment_info = project_info["attachments"]
	attachments_filenames_for_project=[]
	for attachment in attachment_info:
		return_code, file_name = download_attachment(attachment)
		if return_code == 0:
			attachments_filenames_for_project.append(file_name)
		else: 
			print("Error for " + file_name)
	
	# iterate experimental procedure
	experiment_procedures = project_info["experiment_procedures"]
	description = ""
	eLabFTW_prel_links = []
	eLabFTW_prel_links.append("/biocoll/project/" + str(project_belongs_to))
	eLabFTW_prel_links.append("/biocoll/milestones/" + str(ancestry))
	alert_to_check = False
	for exp_proc in experiment_procedures:
		description += "<h2>" + exp_proc["name"] + "</h2>"
		for element in exp_proc["elements"]:
			text, excel_alerting, list_of_files, link_these_eLabFTW = download_elements_experiment_procedures(element["id"])
			description += text
			if excel_alerting:
				alert_to_check = True
			if list_of_files:
				attachments_filenames_for_project = attachments_filenames_for_project + list_of_files
			if link_these_eLabFTW:
				eLabFTW_prel_links = eLabFTW_prel_links + link_these_eLabFTW

	eLabFTW_links = []
	for ID in eLabFTW_prel_links:
		biocoll = ID.split("/")[1]
		collection = ID.split("/")[2]
		if biocoll == "biocoll":
			exp = True
		else: 
			exp = False
		lab_ID = ID.split("/")[3]
		try:
			id_safe = Labguru_eLabFTW_dict[collection][lab_ID]
			if exp:
				id_safe = "experiments_links/"+id_safe
			else:
				id_safe = "items_links/"+id_safe
			eLabFTW_links.append(id_safe)
		except KeyError:
			if ID.split("/")[3] == "None":
				continue
			print("ID " + str(ID) + " not found")

	# prepare for storing file
	eLabFTW_project_data = {"category":26,"title": title, "body": description, "tags": tags}
	eLabFTW_metadata = {"elabftw": {"extra_fields_groups": [{"id": 1, "name": "General info"}, {"id": 2, "name": "Labguru Info"}]}, "extra_fields": {"Owner": {"type":"text", "value":owner, "group_id":1}, "Labguru ID": {"type":"text", "value":labguru_id, "group_id":2}}}
	
	if created_at != "null":
		eLabFTW_metadata["extra_fields"]["created_at"] = {"type":"text", "value":created_at, "group_id":1}
	if updated_at != "null":
		eLabFTW_metadata["extra_fields"]["updated_at"] = {"type":"text", "value":updated_at, "group_id":1}

	# write everything in file to be read and uploaded elsewhere: eLabFTW_project_data, attachments_filenames_for_project, milestones_to_link, experiments_to_link
	eLabFTW_project_data["metadata"] = eLabFTW_metadata
	return 0, eLabFTW_project_data, alert_to_check, eLabFTW_links, attachments_filenames_for_project, comments
	
if __name__ == "__main__":

	projects_file = "../ressourcen/milestones_downloaded.tsv"
	projects_downloaded = []
	if not os.path.isfile(projects_file):
		with open(projects_file, "w") as f:
			f.write("LabguruID\talert_to_check\tfile_name\teLabFTW_links\tattachments_list\tComments\n")
	else:
		with open(projects_file) as f:
			header = True
			for line in f:
				if header: 
					header = False
					continue
				projects_downloaded.append(line.split("\t")[0])
				
	list_of_project_numbers = []
	with open("Labguru_milestone_IDs.tsv") as f:
		header = True
		for line in f:
			if header:
				header = False
				continue
			list_of_project_numbers.append(line.split("\t")[0])

	#project_number = 1009353 # 1009409
			
	counter = 0
	for project_number in list_of_project_numbers:
		print("Now working on milestone " + str(project_number))
		counter += 1
		#if counter == 10:
		#	break
		if project_number in projects_downloaded:
			continue
		else:
			return_code, eLab_json, alertCheck, eLabFTWLinks, attachments_list, comments_list = download_milestone(project_number)
			
			if return_code:
				print("Project number " + str(project_number) + " seems to have failed")	
			else:
				print("Project number " + str(project_number) + " seems to have been a success")
				json_file_name = str(project_number) + ".json"
				with open("../ressourcen/milestone_jsons/" + json_file_name, "w") as jsonf:
					jsonf.write(str(eLab_json))
				with open(projects_file, "a") as f:
					f.write(str(project_number) + "\t" + str(alertCheck) + "\t" + json_file_name + "\t" + str(eLabFTWLinks) + "\t" + str(attachments_list) + "\t" + str(comments_list) + "\n")
