### Labguru IDs are not unique !!! Only unique within collection !!!

with open("LabguruID_eLabFTWID_all.tsv", "w") as f:
	f.write("collection\tLabguruID\teLabFTWID\n")

SysID_to_Labguru_ID = {}
with open("Labguru_plasmidsetc_IDs.tsv") as f:
	header = True
	for line in f:
		if header:
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		collection = split_line[0]
		SysID = split_line[2]
		Labguru_ID = split_line[1]
		if collection not in list(SysID_to_Labguru_ID.keys()):
			SysID_to_Labguru_ID[collection] = {}
			SysID_to_Labguru_ID[collection][SysID] = Labguru_ID
		else:
			SysID_to_Labguru_ID[collection][SysID] = Labguru_ID

with open("../ressourcen/protocols_uploaded.tsv") as f: # LabguruID\teLabFTW_ID\n
	header = True
	for line in f:
		if header:
			header = False
			continue
		with open("LabguruID_eLabFTWID_all.tsv", "a") as f2:
			f2.write("protocols" + "\t" + line.split("\t")[0] + "\t"+ line.strip("\n").split("\t")[1] +"\n")
				
with open("../ressourcen/bacteria_alreadyUploded.tsv") as f: #  SysID\tPlasmid_name\titem_id
	header = True
	for line in f:
		if header:
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		with open("LabguruID_eLabFTWID_all.tsv", "a") as f2:
			f2.write("bacteria" + "\t" + SysID_to_Labguru_ID["bacteria"][split_line[0]] + "\t"+ split_line[2] +"\n")

with open("../ressourcen/alreadyUploded.tsv") as f: #  SysID\tPlasmid_name\tgbk_file\titem_id
	header = True
	for line in f:
		if header:
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		with open("LabguruID_eLabFTWID_all.tsv", "a") as f2:
			f2.write("plasmids" + "\t" + SysID_to_Labguru_ID["plasmids"][split_line[0]] + "\t"+ split_line[3] +"\n")

with open("../ressourcen/antibodies_alreadyUploded.tsv") as f: #  SysID\tAntibody_name\titem_id
	header = True
	for line in f:
		if header:
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		with open("LabguruID_eLabFTWID_all.tsv", "a") as f2:
			f2.write("antibodies" + "\t" + SysID_to_Labguru_ID["antibodies"][split_line[0]] + "\t"+ split_line[2] +"\n")
			
with open("../ressourcen/eLabFTW_projects_uploaded.tsv") as f:
	header = True
	for line in f:
		if header:
			header = False
			continue
		split_line = line.strip("\n").split("\t")
		with open("LabguruID_eLabFTWID_all.tsv", "a") as f2:
			f2.write("project\t" + split_line[0] + "\t"+ split_line[1] +"\n")
