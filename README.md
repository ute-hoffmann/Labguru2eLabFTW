# Labguru2eLabFTW: some code snippets for transferring Labguru data to eLabFTW

[eLabFTW](https://www.elabftw.net/) is a free and open source electronic lab notebook. Here, I collect some code to migrate data from Labguru to eLabFTW. In this pursuit, the [python library](https://github.com/elabftw/elabapi-python/) for the [eLabFTW REST API](https://doc.elabftw.net/api/v2/) was used and the requests library to access both eLabFTW as well as Labguru (via the [Labguru API](https://my.labguru.com/api-docs/index.html?urls.primaryName=API%20V1%20Docs#/), [how to get a token](https://help.labguru.com/en/articles/1492443-how-to-generate-a-personal-token)).

Most code needs the file "client.py" from the [python library](https://github.com/elabftw/elabapi-python/) for the [eLabFTW REST API](https://doc.elabftw.net/api/v2/).

The code in this repository can maybe help others facing a similar task to have a place to start from. It is far from ideal and there are some issues which occured during the transfer. 

Here is a step-by-step description of how data was migrated plus comments how this could have been done better:
- Antibodies, Plasmids, Bacteria and similar items were downloaded as table instead of through the Labguru API - hence, some data went missing. These were uploaded to eLabFTW. Plasmids and bacteria were stored in the eLabFTW inventory. Plasmid code also includes code to identify gbk files corresponding to the plasmids. Later, plasmid attachments were downloaded and uploaded separately ([3_Labguru_eLabFTW_tryToGetPlasmidAttachment.py](3_Labguru_eLabFTW_tryToGetPlasmidAttachment.py))
- the "storage_unit_number" of an inventory box can be found by hovering over the respective box in the eLabFTW GUI
- in a next step, protocols were downloaded from Labguru through its API and uploaded to eLabFTW
- then, the main pages of projects were downloaded and uploaded - at this point, a huge table with Labguru ID -> eLabFTW ID was created to link antibodies, plasmids, bacteria, protocols etc. to milestones and experiments, which were downloaded and then uploaded in the next step and the one after
- Generally, I was not able to include images, which had been part of the text in Labguru, into the text in eLabFTW and they were attached to entries. Also, excel files were omitted. Other experiment elements include "Samples and reagents" - in most cases, I was able to parse this information via json - however, for approx. 200/6000 experiments, this did not work. Finally, there were many cases of https status 500. Some code in this repository deals with these by relatively proper error handlling, some code does not and the instances have to be skipped manually
- at some point, links between entries and protocols etc. were added manually ([labguru_identify_links_protocols.py](labguru_identify_links_protocols.py) and [eLabFTW_createLink.py](eLabFTW_createLink.py))
