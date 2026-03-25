# list of bacteria
name_plasmid_csv = "../ressourcen/allesAndere/2026-02-12_at_11_22_00331AM_Bacterium.csv"
fixed_file =  "../ressourcen/allesAndere/2026-02-12_at_11_22_00331AM_Bacterium_readyToUpload.csv"

header_plasmid_file = "System ID	Title	Strain	Sensitivity	Owner	Source	Created at	Manufacturer	Catalog no.	Units remarks	Web page	Price	Currency	Produced by	Size	Size unit	Description	Tags	Database ID	Reference	Genotype	GMO	Transformed Vector	Stock ID	Stock name	Privacy	Stock type	Stock color	Stock description	Stock concentration	Concentration units	Concentration remarks	Stock volume	Volume units	Volume remarks	Stock weight	Weight units	Weight remarks	Stock units	Stock count	Stock lot	Stock barcode	Stock expiry date	Stock owner	Stored / frozen by	Stored / frozen on	Created at	Box name	Box dimensions - # rows	Box dimensions - # columns	Box location in Rack - Cells	Stock position	Storage location	Consumed by	Consumed on"
length_line = len(header_plasmid_file.split("\t"))

counter = 0
with open(name_plasmid_csv) as f: 
	with open(fixed_file, "w") as f2:
		new_line = ""
		for line in f:
			split_line = line.replace('\t', ' ').strip("\n").split(";") # replace tab bei space so that we can use tab as delimiter later, strip line break, split at ;, because this is the field delimiter we are using
			if new_line: # if there is already a line which began, add the next line in the file 
				new_line = new_line[:-1]
				new_line += " " + split_line[0] + "\t" # replace "\n" by " " and start new cell
				for part in split_line[1:]:
					new_line += part + "\t"
				if len(new_line[:-1].split("\t")) == length_line:
					f2.write(new_line[:-1] + "\n")
					new_line = ""
				if len(new_line[:-1].split("\t")) > length_line:
					print("Problem with:")
					print(new_line.split("\t")[0])
					#print(new_line)
					#print(line)
					#print(header_plasmid_file.split("\t")[24])
					print("length new line")
					print(len(new_line[:-1].split("\t")))
					print(length_line)
					print("\n")
					break
			else:
				for part in split_line:
					new_line += part + "\t"
				if len(new_line[:-1].split("\t")) == length_line:
					f2.write(new_line[:-1] + "\n")
					new_line = ""
