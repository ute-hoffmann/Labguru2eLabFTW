# needs correct mamba environment; before running script run:  
# mamba activate API 

# read which boxes exist
# !! check that Plasmid boxes etc. are correct ! (Plasmid DB over 40, I think)
boxes_dict = {}
with open("dict_numbers_places.txt") as inventory_file:
	header = True
	for line in inventory_file:
		if header:
			header = False
		split_line = line.strip("\n").split(";")
		boxes_dict[split_line[0]] = [split_line[1], split_line[2]]

### Processing of plasmid csv, return dict with info

# Plasmids can be downloaded as csv from Labguru
# cells may contain \t or \n -> open once in Office, save as Office file, find all semicolons (;) and replace by commas (,) , export as .csv and use semicolon (;) as cell separator
# open with fix_csv.py to remove line breaks in the middle of lines
# check columns given by Labguru again, e.g. Feb. 2026: title was renamed to name *

name_plasmid_csv = "../ressourcen/2025-12-03_at_10_54_09984AM_Plasmid_smallSubset.csv"
#name_plasmid_csv = "../ressourcen/2025-12-03_at_10_54_09984AM_Plasmid_fixed.csv"
name_plasmid_csv="../ressourcen/2026-02-12_at_09_46_34573AM_Plasmid_semiColonsFixed_fixedRest_readyUpload.csv"

# Columns present in csv and what to do with them
header_plasmid_file = "System ID	title	Alternative name	Base vector	Length	Host	Usage	Resistance	Insert	Clone number	Owner	Source	Plasmid created at	Manufacturer	Catalog no.	Units remarks	Web page	Price	Currency	Produced by	Size	Size unit	Description	tags	Sequence	Sequence name	Sequence type	Sequence organism	Sequence accession	Sequence description	Primers used	Cloned with	Stock ID	Stock name	Privacy	Stock type	Stock color	Stock description	Stock concentration	Concentration units	Concentration remarks	Stock volume	Volume units	Volume remarks	Stock weight	Weight units	Weight remarks	Stock units	Stock count	Stock lot	Stock barcode	Stock expiry date	Stock owner	Stored / frozen by	Stored / frozen on	Stock created at	Box name	Box dimensions - # rows	Box dimensions - # columns	Box location in Rack - Cells	Stock position	Storage location	Consumed by	Consumed on"
skip_columns = "Sequence	Sequence name	Sequence type	Clone number	Price	Currency	Size	Size unit	Sequence type	Sequence organism	Privacy	Stock type	Stock color	Stock volume	Volume units	Volume remarks	Stock weight	Weight units	Weight remarks	Stock units	Stock count	Stock lot	Stock barcode	Stock expiry date	Box dimensions - # rows	Box dimensions - # rows	Box dimensions - # columns	Box location in Rack - Cells	Storage location	Consumed by	Consumed on"
all_about_stocks = "Stock ID	Stock name	Stock description	Stock concentration	Concentration units	Concentration remarks	Stock owner	Stored / frozen by	Stored / frozen on	Stock created at	Box name	Box location in Rack - Cells	Stock position	Storage location" # partially redundant with skip_columns, but skip_columns is tested first -> these are skipped anyways
split_header_plasmid_file = header_plasmid_file.split("\t")

def extract_all_info(split_line_list): # takes [list] of all parts of row
	return_dict = {}
	container_dict = {}
	container_dict[1] = {}
	for counter in range(len(split_header_plasmid_file)): # go through all columns
		# skip the columns which are not of relevance for us
		if split_header_plasmid_file[counter] in skip_columns.split("\t"):
			continue
		# feed into container_dict info about stock, if there is info about stock
		elif split_header_plasmid_file[counter] in all_about_stocks.split("\t"):
			if split_line_list[counter]:
				container_dict[1][split_header_plasmid_file[counter]] = split_line_list[counter]
				continue
		# feed rest of info into return_dict
		elif split_line[counter]:
			if split_line_list[counter]:
				return_dict[split_header_plasmid_file[counter]] = split_line_list[counter]
	return_dict["containers"] = container_dict
	return return_dict, container_dict[1]
	
plasmid_dict = {}
counter = 0
with open(name_plasmid_csv) as plasmid_file:
	header = True
	for line in plasmid_file:
		if header:
			header = False
			continue
		split_line = line.replace('\ufeff', '').strip("\n").split("\t")
		# how to handle duplicate entries? -> usually, I guess, issue of containers in several different places -> add dict of containers -> kick out plasmids stored in "non-canonically locations"
		# System.ID is repeated in these cases
		systemID = split_line[0]
		
		# extract info from line
		try:
			# line_dict contains info about everything, contain_dict is specific for stock described in this line
			line_dict, contain_dict = extract_all_info(split_line)
		except IndexError:
			continue
		try: # kick out plasmids with unknown storage location and in private boxes
			if not (contain_dict["Box name"] in list(boxes_dict.keys())):
				print(contain_dict["Box name"] + " not in list of known plasmid boxes")
				continue
		except KeyError:
			print("KeyError for SysID " + str(systemID))
			print(contain_dict)
			continue
		if systemID in plasmid_dict.keys():
			current_number = len(plasmid_dict[systemID]["containers"])
			plasmid_dict[systemID]["containers"][current_number+1] = contain_dict
		else:
			plasmid_dict[systemID] = line_dict


# create dict of plasmids that were already uploaded:
uploaded_plasmids = {}
with open("../ressourcen/alreadyUploded.tsv") as uploaded_f:
	header = True
	for line in uploaded_f:
		if header:
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		uploaded_plasmids[split_line[0]] = [split_line[1], int(split_line[3]), split_line[2]] # [sysID] -> [plasmid name, eLabFTW ID, gbk name]
			
### find .gbk file for plasmid
from os import listdir
from os.path import isfile, join

plasmid_folder = "../ressourcen/Plasmids export"
list_files_plasmids_folder = [f for f in listdir(plasmid_folder) if isfile(join(plasmid_folder, f))]

for SysID in plasmid_dict.keys():
	# check if already uploaded - skip these plasmids
	if SysID in list(uploaded_plasmids.keys()):
		print("Plasmid SysID " + SysID + ", name: " + uploaded_plasmids[SysID][0] + " was already uploaded under ID " + str(uploaded_plasmids[SysID][1]) + " - skipping this plasmid")
		continue
	try:
		name = plasmid_dict[SysID]["title"]
	except KeyError:
		print(str(SysID) + " no title found????")
		continue
	list_of_potential_gbk = []
	for f in list_files_plasmids_folder:
		if name in f:
			print(name + " and " + f)
			list_of_potential_gbk.append(f)
			
	gbk_file = ""
	if len(list_of_potential_gbk) > 1:
		print("Found several gbk files which might be correct:")
		for counter in range(len(list_of_potential_gbk)):
			print(str(counter) + "\t" + str(list_of_potential_gbk[counter]))
		try:
			user_input = input("Please give number of correct file or press X if none is correct, press C to exit program: ")
			if user_input == "X":
				continue
			elif user_input == "C":
				break
			else:
				gbk_file = list_of_potential_gbk[int(user_input)]
				print(gbk_file + " was chosen")
		except IndexError:
			print("Probably wrong number pressed, this is what you wrote: " + user_input + "\nI decided to assign no gbk file to plasmid")
	elif len(list_of_potential_gbk) < 1:
		print("No gbk found for " + name)
	else:
		gbk_file = list_of_potential_gbk[0]
		
	plasmid_dict[SysID]["gbk_file"] = gbk_file
		
### print table with attached gbk files? complicated, to be honest -> print whole dict and try to read dict?
with open("../ressourcen/2025-12-17_plasmids_dict.txt", "w") as output_f:
	output_f.write(str(plasmid_dict))

### Upload 
# maybe create table with plasmids and if they were already uploaded? Or if they already have an ID in eLabFTW?
import elabapi_python
from client import api_client, API_KEY, API_HOST
import json
import requests

# Header for request via requests library
header_requests = {
	"Authorization": API_KEY,  # API TOKEN
	"Content-Type": "application/json",
}
# Payload for the  POST request (to adapt)
payload_requests = {
	"qty_stored": "1",
	"qty_unit": "tube"
}

# put check here if already uploaded
resourcesCategoriesApi = elabapi_python.ResourcesCategoriesApi(api_client)
TEAM_ID = "current"
try:
    # Fetch the resources categories from the API
    resources_categories = resourcesCategoriesApi.read_team_resources_categories(TEAM_ID)

    # Print the number of categories
    print(f"Number of categories: {len(resources_categories)}")

    # Iterate through each category and display the ID and Title
    for resource_category in resources_categories:
        print(f"ID: {resource_category.id}, Title: {resource_category.title}")

# Error handling for API requests
except elabapi_python.rest.ApiException as e:
    print(f"Error fetching categories or entries: {e}")

items_client = elabapi_python.ItemsApi(api_client)
with open("../ressourcen/alreadyUploded.tsv", "a") as uploaded_f:
	#uploaded_f.write("SysID\tPlasmid_name\tgbk_file\titem_id\n") # uncomment if file does not exist yet
	for SysID in plasmid_dict.keys():
		# check if already uploaded - skip these plasmids
		if SysID in list(uploaded_plasmids.keys()):
			print("Plasmid SysID " + SysID + ", name: " + uploaded_plasmids[SysID][0] + " was already uploaded under ID " + str(uploaded_plasmids[SysID][1]) + " - skipping this plasmid")
			continue
		
		plasmid_title = plasmid_dict[SysID]["title"]
		data={"category":13,"title":plasmid_dict[SysID]["title"]}
		
		metadata = {"elabftw": {"extra_fields_groups": [{"id": 1, "name": "General info"}]}, "extra_fields": {}}
		
		gbk_file = ""
		for info in plasmid_dict[SysID]:
			if info == "containers":
				continue
			elif info == "System ID":
				continue # not important for us
			elif info == "title":
				continue # add this as title (see above)
			elif info == "tags":
				data["tags"] = plasmid_dict[SysID][info].split(",")
				continue # add this as tags
			elif info == "Description":
				data["body"] = plasmid_dict[SysID][info]
				continue # add this as Description
			elif info == "gbk_file":
				gbk_file = plasmid_dict[SysID][info]
			else:
				metadata["extra_fields"][info] = {"type":"text","value":plasmid_dict[SysID][info],"group_id":1}
		
		# add extra field group for each container
		storage_id = [] # initialize variable
		
		if "containers" in list(plasmid_dict[SysID]):
			for container in plasmid_dict[SysID]["containers"]:
				group_ID = container+1
				container_info = {}
				name = "Stock " + str(container)
				metadata["elabftw"]["extra_fields_groups"].append({"id":group_ID, "name":name})
				for item in plasmid_dict[SysID]["containers"][container]:
					if item == "Box name":
						try:
							storage_id.append(int(boxes_dict[plasmid_dict[SysID]["containers"][container]["Box name"]][1]))
						except KeyError:
							print(plasmid_dict[SysID]["containers"][container]["Box name"] + " was not found in boxes dict")
					if item == "Volume units": # most likely irrelevant since not read in anymore above
						continue
					if item == "Stock volume": # most likely irrelevant since not read in anymore above
						try:
							units = plasmid_dict[SysID]["containers"]["Volume units"]
						except KeyError:
							units = "ml"
						metadata["extra_fields"][name + " volume"] = {"type": "number", "value":plasmid_dict[SysID]["containers"][container][item], "unit":units, "group_id": group_ID}
					else:
						metadata["extra_fields"][name + " " + item] = {"type": "text", "value":plasmid_dict[SysID]["containers"][container][item], "group_id": group_ID}

		# now create a Resource with this metadata
		data["metadata"] = metadata

		response_data, status_code, headers = items_client.post_item_with_http_info(body=data)
		item_id = int(headers.get('Location').split('/').pop())
		
		if status_code == 201:
    			print(f"[*] We created a Resource with ID: {item_id}")
		else:
    			print(status_code)
    				
    		# upload gbk file	
		if gbk_file:
			uploadsApi = elabapi_python.UploadsApi(api_client)
	
			# upload a file in a specific directory to a existing experiment entry (e.g. with ID 399)
			local_file_path = "../ressourcen/Plasmids export/" + gbk_file
			uploadsApi.post_upload('items', item_id, file=local_file_path, comment='gbk from cloneManager')
		
		# add stock to inventory

		if storage_id:
			for location in storage_id:
				r = requests.post(
					f"{API_HOST}/items/{item_id}/containers/{location}",
					headers=header_requests,
					json=payload_requests
					)
				if r.status_code == 201 or r.status_code == 200:
					print("Plasmid stored successfully")
				else:
					print(f"Status: {r.status_code}")

		uploaded_f.write(str(SysID) + "\t" + plasmid_title + "\t" + gbk_file + "\t" + str(item_id) + "\n")
		
