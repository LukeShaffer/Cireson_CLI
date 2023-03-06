'''
This script loads in input text or csv file containing the names of 
all Cireson assets to be reconciled and creates a dynamic list of 
settings.computerObj's out of them, only adding the computers if each
of the specified fields has valid data

Fair warning, this file so far does not load in 
'''

import sys
import settings
from settings import computerObj
import argparse




#textfile to list

def textToObj():

	#set up this file to take positional and optional commandline arguments
	parser=argparse.ArgumentParser(description="Checks an input file for model, serial, PCN, status, type, name, locationDetail, organization, and user errors."
		" These MUST be specified in the following order: model,serial,PCN,status,assetType,name,locDetail,organization,user")
	parser.add_argument("path",help="Path of the file to be checked")
	parser.add_argument("-v","--verbose",help="Print all error messages as they occur"
		,action="store_true")
	args=parser.parse_args()

	if args.verbose:
		settings.verbose=True



	#start of file
	#set hardcoded asset information taken from Cireson to check new computers against
	statusTypes =('Ordered','Received','In Stock','On Hold',
			'Repurpose Inventory','Repair, Test, Etc.','Salvage Inventory',
			'Deployed','Primary','Secondary','TA / FA','Computing Lab', 
			'Teaching Station','Signage','Offsite','Server','Other','Virtual Machine',
			'Student Worker','Departmental','Loaned','Retired','Lost/Stolen','Disposed')

	assetTypes = ('Computer','Virtual Machine','Tablet','Computer Peripheral','Printer','Scanner',
			'Monitor','Touch Display','Projector','Camera','Digital Lab Equipment',
			'A/V Loan Equipment','Point-of-Sale Equipment','Networking Equipment')

	#for collecting computer objects and error lines
	computerList = list()
	modelErrors=list()
	serialErrors = list()
	pcnErrors= list()
	statusErrors=list()
	typeErrors=list()
	nameErorrs=list()
	locationDetailsErrors=list()
	organizationErrors=list()
	userErrors=list()

	#default delimiter is tab, will check for CSV via supplied filename ext
	delimiter = '\t'
	fileName=args.path
	if '.csv' in fileName:
		delimiter = ','

	contents=open(fileName,'r')
	nextLine = contents.readline() #skip the headers
	moreText = True
	count = 2

	while moreText ==True:
		nextLine = contents.readline()

		#we have some arbitrary line in the textfile
		if '\n' in nextLine:
			#skip lines created by multiple concurrent runs
			parts = nextLine.split(delimiter)
			newComputer = computerObj()

			#error handling for each data member
			#check that there are 9 members on a line, and if not skip the line
			try:
				newComputer.model = parts[0]
				newComputer.serial = parts[1]
				newComputer.PCN=parts[2]
				newComputer.status=parts[3]
				newComputer.assetType=parts[4]
				newComputer.name=parts[5]
				newComputer.locDetail=parts[6]
				newComputer.room=parts[6]
				newComputer.organization=parts[7]
				newComputer.user=parts[8]

			except IndexError: #if one line does not have 9 members, skip the line and take note, but continue
				print(newComputer.toString())
				if settings.verbose:
					print("@!#@#Error, line "+str(count)+" has fewer than 9 valid entries")
				count+=1
				continue

			#now check each member for errors

			#model
			if parts[0] is '':
				parts[0] = '<None>'
				modelErrors.append(count)
				if settings.verbose:
					print('\nModel ERROR on line: '+str(count)+ ' Read Status: ' +parts[0]+'\n')
				count+=1
				continue

			#serial
			if len(parts[1])<7:
				if parts[1] is '':
					parts[1] = '<None>'
				serialErrors.append(count)
				if settings.verbose:
					print('\nSerial ERROR on line: '+str(count)+ ' Read Serial: ' +parts[1]+'\n')
				count+=1
				continue
			#PCN
			if parts[2] is '':
				parts[2] = '<None>'
				if settings.verbose:
					print('\nPCN ERROR on line: '+str(count)+ ' Read PCN: ' +parts[2]+'\n')
				count+=1
				continue
			try:
	   			val = int(parts[2])

			except ValueError:
				pcnErrors.append(count)
				if settings.verbose:
					print('\nPCN ERROR on line: '+str(count)+ ' Read PCN: ' +parts[2]+'\n')
				count+=1
				continue
			
			#status
			if parts[3] is '':
				parts[3] = '<None>'

			if parts[3] in statusTypes: #read status is valid
				1+1
			else:
				statusErrors.append(count)
				if parts[3] is '':
					parts[3] = '<None>'
				if settings.verbose:
					print('\nSTATUS ERROR on line: '+str(count)+ ' Read Status: ' +parts[3]+'\n')
				count+=1
				continue
			#type
			if parts[4] in assetTypes: #read asset type is valid
				1+1
			else:
				typeErrors.append(count)
				if settings.verbose:
					print('\nTYPE ERROR on line: '+str(count)+ ' Read type: ' +parts[4]+'\n')
				count+=1
				continue
			#name
			if len(parts[5]) <3:	#arbitrary length requirement
				if parts[5] is '':
					parts[5] = '<None>'
				nameErorrs.append(count)
				if settings.verbose:
					print('\nNAME ERROR on line: '+str(count)+ ' Read name: ' +parts[5]+'\n')
				count+=1
				continue
			#location details
			if parts[6] is '':
				parts[6] = '<None>'
				locationDetailsErrors.append(count)
				if settings.verbose:
					print('\nLOCATION DETAIL ERROR on line: '+str(count)+ ' Read location detail: ' +parts[6]+'\n')
				count+=1
				continue
			#organization
			if parts[7] is '':
				parts[7] = '<None>'
				organizationErrors.append(count)
				if settings.verbose:
					print('\nORGANIZATION ERROR on line: '+str(count)+ ' Read organization: ' +parts[7]+'\n')
				count+=1
				continue
			#user
			if parts[8] is '':
				parts[8] = '<None>'
				userErrors.append(count)
				if settings.verbose:
					print('\nUSER ERROR on line: '+str(count)+ ' Read user: ' +parts[8]+'\n')
				count+=1
				continue

			#The world is not yet ready for this much cleanup
			if 'local_users' in parts[8]:
				userErrors.append(count)
				if settings.verbose:
					print('\nUSER ERROR on line: '+str(count)+ ' Read user: ' +parts[8]+'\n')
				count+=1
				continue
				

			#we have success on this line
			newComputer.lineNumber=count
			if settings.verbose:
				print(str(count)+': '+ newComputer.toString())
			count+=1
			computerList.append(newComputer)

		else:#we have the last line
			if settings.verbose:
				print("NOT CHECKED::content: " + nextLine)
			moreText =False

	print('\n--<<INPUT FILE RESULTS>>--\n')
	print("lines scanned: " + str(count-1))
	print("valid computers: "+ str(len(computerList)))
	print("Success rate: " + str( (len(computerList)/(count-2))*100 ) + '%')
	if settings.verbose:
		print('\nERROR SUMMARY\n\n')
		print("lines with Serial error (length<7): ")
		print(serialErrors[:])

		print("\nLines with PCN error: ")
		print(pcnErrors[:])

		print("\nLines with asset status error: ")
		print("NOTE: Asset status must match those provided in Cireson EXACTLY to not fail")
		print(statusErrors[:])

		print("\nLines with type error: ")
		print("NOTE: Asset type must match those provided in Cireson EXACTLY to not fail")

		print(typeErrors[:])

		print("\nLines with name errors: ")
		print(nameErorrs[:])

		print("\nLines with location detail errors: ")
		print(locationDetailsErrors[:])

		print("\nLines with organization errors: ")
		print(organizationErrors[:])

		print("\nLines with user errors: ")
		print(userErrors[:])

	contents.close()
	return computerList

#do the check if this script was called individually
if 'checkInputFile' in sys.argv[0]:
	textToObj()