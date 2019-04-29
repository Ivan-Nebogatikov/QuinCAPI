# Version: .3, sql query, port check
# Date: 4/29/2019
#
# In Windows Explorer, drag-and-drop a set of files onto this script's icon
# This script will do the following:
# 1. Prompt to create a new case or use an existing one
# 2. Attempt to identify the type of evidence dropped on the script
# 3. Process the evidence into the specified case
#
# Items dropped on this script must belong to ONE of the following categories:
# - The first segment of a forensic image file
# - Any number of native files
#
# IMPORTANT:
# EntAPICommon.py must reside in the same folder as this script.
# Make sure to update APIkey, APIhostname, and ProjectData.

import sys
import os
import EntAPICommon

# UPDATE THESE
APIkey = "84af3650-176a-4edf-bad8-25ad5b708f37" # Generated in Enterprise via Tools > Access API Key
APIhostname = "WIN-B3VKJBVM6RQ" # Machine (name or IP) running Enterprise and Quin-C Self Host Service
ProjectData = "\\\\WIN-B3VKJBVM6RQ\\AccessData\\ProjectData" # Default case data path, make sure to escape any backslashes

# Connection test
if EntAPICommon.IsApiUp(APIhostname):
    print("OK")
else:
    print("Failed")
    print("Check the 'Quin-C Self Host Service' on %s" % APIhostname)
    os.system("pause")
    raise SystemExit

# Grab a list of all the item dropped onto the script
print()
items = []
for i in range(1,len(sys.argv)):
    items.append(sys.argv[i])
# Sort for easier to read output
items.sort()

print("Items to process: ")
for item in items:
    print(item)

print()
print("Please review the items listed before continuing.")
print("Supported file types:")
print("- First segment of a forensic image")
print("- Individual native files")
print("Note: The Processing Engine must have access to all paths listed.")
os.system("pause")

# Prompt for case to process into
print()
choice = ''
while choice not in ['1','2']:
    print("Choose from the following:")
    print("1 - Process into a new case")
    print("2 - Process into an existing case")
    choice = input("Enter 1 or 2: ")
    if choice not in ['1','2']:
        print("Invalid selection!")

if choice == '1':
    # Prompt for a case name
    print()
    print("Case data will be stored at '%s'" % ProjectData)
    CaseName = input("Enter your desired case name: ")

    # Create the case and get the CaseID
    # TODO: Get the CaseID for an existing case
    print()
    print("Creating case '%s'..." % CaseName)
    ProjectData = ProjectData + "\\" + CaseName
    JobData = ProjectData + "\\JobData"

    if not os.path.exists(ProjectData):
        os.makedirs(ProjectData)

    if not os.path.exists(JobData):
        os.makedirs(JobData)

    createcaseDefinition = {
    "name": CaseName,
    "ftkCaseFolderPath": ProjectData,
    "responsiveFilePath": JobData,
    "processingMode": 2
    }

    CaseID = EntAPICommon.CreateCase(APIkey, APIhostname, createcaseDefinition)
    print("Case ID: %s" % CaseID)
    print("Project folder: %s" % ProjectData)
elif choice == '2':
    print()
    CaseID = input("Enter the desired case's Case ID: ")
    # TODO: Check if Case ID exist
    # TODO: Use case name to get case id

# Iterate through all input paths
# If we detect a first image segment, we'll process its image
# Otherwise, treat everything as natives
print()
for item in items:
    EvidenceType = EntAPICommon.DetectEvidenceType(item)
    if EvidenceType == 2:
        definition = {
            "evidenceToCreate": {
                "evidenceType": EvidenceType,
                "evidencePath": item
            }
        }
        print("Started processing image '%s'" % item)
        print(EntAPICommon.AddEvidence(APIkey, APIhostname, CaseID, definition))
    elif EvidenceType == 0:
        definition = {
            "evidenceToCreate": {
                "evidenceType": EvidenceType,
                "evidencePath": item
            }
        }
        print("Started processing native '%s'" % item)
        print(EntAPICommon.AddEvidence(APIkey, APIhostname, CaseID, definition))    
    else:
        print("I do not know how to handle that evidence.")
print("Monitor job progress by opening case %s and going to View > Progress Window" % CaseID)
os.system("pause")
