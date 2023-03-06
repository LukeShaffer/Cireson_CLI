from checkInputFile import textToObj
import settings
from settings import computerObj
import time
import re
import itertools
import sys #os check for zip/izip compatibility

settings.verbose = False


'''
this function is meant to parse the value of a provided key and to 
extract the "sub-key value" pair from that, since the cireson hwJson 
object bundles lots of attributes together in various key-value arrangements
'''
def extractValueFromDict(dictionary,key,subKey):
	parseValue = dictionary[key]
	parseValue = parseValue.split(",")
	for search in parseValue:
		if subKey in search:
			#clean it up
			search=search.split(':')

			#search is a list of the form 'key:value', so cut away the key
			#sometimes the values have :'s within them, so slice to account
			#for that
			search=search[1:]

			#now format it pretty
			search = str(search)
			search = search.replace("'","")
			search=search.replace('[','')
			search=search.replace(']','')
			#in python2, unicode strings come out with a 'u' appended to the front of their names
			if search[0]=='u':
				search=search[1:]

			#trim trailing spaces
			if search[-1:] ==' ':
				search = search[0:-1]

			return(search)
	#if we get to this point there is no subkey in the value
	print('Error: '+subKey+' not found in '+key)
	


'''
This function takes in the results of a Cireson inventory query (initial
popup search) and parses over it to extract the internal search ID of each 
computer returned in the search to do an actual detailed search


'''


#Old Method that only returned first match
'''
def getSearchID(responseString):
	text = responseString.split('"')

	#these flags determine if the next key will be the id or name
	IdFlag = False
	nameFlag = False

	tempID = 'dummy'
	tempName = 'dummy name'

	#iterate through the results and save id and names
	#WARNING, this function does not account for duplicates in Cireson yet
	for x in list(text):
		#skip all symbols and only save names and search ID's
		if ':' in x:
			continue
		elif ',' in x:
			continue
		elif '{' in x:
			continue
		elif '}' in x:
			continue
		elif 'Id' == x:
			IdFlag = True
		elif 'DisplayName' in x:
			nameFlag = True
		elif IdFlag is True:
			tempID = x
			IdFlag = False
		elif nameFlag is True:
			tempName =x
			nameFlag = False
		elif tempID != 'dummy' and tempName != 'dummy name':
			return tempID		

	#catch one last one that may have gotten away
	if tempID != 'dummy' and tempName != 'dummy name':
			computerDict[tempName] = tempID
			tempName = 'dummy name'
			tempID = 'dummy'
'''


'''
this function takes the results of a Cireson detail search and creates
an in-house computer object to model it that I can use in other aspects 
of this program

As an input, it will take the entire detailed Cireson response and distill it
down to the single line that contains the hwJson variable that is returned with
the webpage
'''
def parseCiresonHardwareResponse(detailedCiresonResponse):
	hardwarePage=''

	#use StringIO to iterate over lines in the string response
	detailedCiresonResponse = iter(detailedCiresonResponse.splitlines())

	for num, line in enumerate(detailedCiresonResponse):
		if 'hwJson' not in line:
			#print("line"+str(num)+": "+line)
			continue
		else:
			hardwarePage = line
			break

	ciresonHardwareList = list()
	newResponseComputer = computerObj()

	#global removal of symbols
	#I have taken this out because some of the computer model names contain
	#periods and commas for some reason
	#hardwarePage = re.sub('[{}:,]','',hardwarePage)
	#hardwarePage = re.sub('[]','',hardwarePage)

	#each key and value is contained in double quotes, so I split to get every
	#element as separate element
	hardwarePage = hardwarePage.split('"')

	#global removal of empty items, commented out for a similar reason ^
	#hardwarePage = list(filter(None,hardwarePage))

	#placeholder list to copy reformated entries into
	newList = list()
	#string to hold multiple elements of the old list until print conditions are met
	printLine=''
	printLineHoldsData = False

	#create an iterator to traverse the list of attributes
	it = iter(hardwarePage)

	#append all single symbols to the beginning of the next line
	for x in it:
		#add single digits right away, like for room numbers
		if x.isdigit():
			#print("appending digit: "+printLine+x)
			newList.append(printLine+x)
			printLine=''
			printLineHoldsData =False
			continue
		#if we find a key that has an empty value, add the empty value
		if x is '':
			if printLineHoldsData == False:
				#print("found empty key-value, appending none")
				newList.append("<none>")
			else:
				printLine+=x
		if len(x) ==1:
			if printLineHoldsData == False:
				printLine = x
				printLineHoldsData =True
			else:
				printLine+=x
		elif len(x) >1:
			if printLineHoldsData:
				#print("appending data:"+printLine+x)
				newList.append(printLine+x)
				printLine=''
				printLineHoldsData =False
			else:
				#print("appending line: "+x)
				newList.append(x)


	#copy the placeholder list into our working list
	hardwarePage = newList

	#reset newList to clear leading commas, clear remove hardwarePage list 
	#as well because they are "aliases"
	newList =list()


	#make the list iterable, this solves a problem that I don't remember
	it = iter(hardwarePage)
	#outfile=open('hardwareAttributes.txt','w')
	#next(it)

	#keep track of open and close braces
	parenCount =0
	printString =''
	parensEncountered =False
	#if the key item has been added 
	firstElemAdded =False
	#this loop lumps all the JS data members with their values, 
	#along with the line number of where the data member is first encountered

	for i,x in enumerate(it):
		#skip the 'hwJson ='
		if i > 0:
			if '{' in x:
				for char in x:
					if char == '{':
						parenCount+=1
				parensEncountered =True
				printString+=x
				firstElemAdded =True
			if '}' in x:
				for char in x:
					if char == '}':
						parenCount-=1
				printString+=(" "+x)

			if parenCount ==0:
				#if we are printing a regular key
				if parensEncountered ==False:
					newList.append(x)
					#outfile.write(str(i)+": "+x+'\r\n')
				#if we have encountered a set of parenthesis in the value object
				elif parensEncountered == True:
					newList.append(printString)
					#outfile.write(str(i)+": "+printString+'\r\n')
					printString=''
					parensEncountered =False
			#if we have encountered a sub-set of brackets in the value
			elif parenCount >0:
				if firstElemAdded ==False:
					printString+=(" "+x)
			firstElemAdded =False


	#reset lists to clear leading commas and :'s
	hardwarePage=newList
	newList=list()
	it =iter(hardwarePage)

	#if the line starts or ends with a comma, remove it because it doesn't do anything
	for x in it:
		#print(x)
		#if we have found a key that has an empty value
		if x.startswith(":,"):
			newList.append("")
			x=x[2:]
		if x.startswith(": ,"): #this occurs when the room item in cireson is blank
			x=x[3:]
			newList.append("<None>")
		if x.startswith(",")  or x.startswith(":"):
			x=x[1:]
		if x[-1:] == ',':
			x=x[0:-1]
		newList.append(x)


	hardwarePage = newList
	#troubleshooting V
	'''
	print("Hardware List:")
	for x in newList:
		print(x)
		'''
	#hardwarePage is now a list of key:value 's 
	#now convert it into an equivalent dictionary
	if sys.version_info.major==2:
		computerDict = dict(itertools.izip_longest(*[iter(newList)] * 2, fillvalue=""))
	else:
		computerDict = dict(itertools.zip_longest(*[iter(newList)] * 2, fillvalue=""))


	'''
	#troubleshooting V
	for item in computerDict:
		print(item,computerDict[item])
	print("Asset Status: "+computerDict['HardwareAssetStatus'])
	print('Extracted Asset Status:'+extractValueFromDict(computerDict,'HardwareAssetStatus','Name'))

	print("Dict is as follows:")

	for k,v in computerDict.items():
		print(k, v)
	'''

	#if there is a mismatch between the display name and regular name,
	#prompt the user to chose which one they want
	try:
		if computerDict['DisplayName'] != computerDict['Name']:
			1+1
	except:
		return None

	if computerDict['DisplayName'] != computerDict['Name']:
		print("Warning: Displayname mismatch for computer with PCN: "+computerDict['AssetTag'])
		print("would you like to use the (1)DisplayName <"+
		computerDict['DisplayName'] +">, or (2)Name <"+
		computerDict['Name']+ "> of the computer?")

		validInput=False

		while validInput ==False:
			nameChoice=input()

			#if the DisplayName is what they want, just override the name
			#slot so I dont have to change anything later
			if nameChoice is '1':
				validInput=True
				computerDict['Name'] = computerDict['DisplayName']
			elif nameChoice is '2':
				validInput=True
				#do nothing, because we use name by default anyway
			else:
				print("Please enter a valid input, 1 or 2 ")


	else:
		#print("DisplayName and Name are the same for computer: "+ computerDict['Name'])
		1+1



	#format the computerDict entries into a new computer object and return

	#newResponseComputer.searchID = '00000000-0000-0000-0000-000000000000'#the id given by the xml lookup is cated directly to https://service.REDACTED.asu.edu/AssetManagement/HardwareAsset/Edit/
	newResponseComputer.PCN=computerDict['AssetTag']
	newResponseComputer.serial=computerDict['SerialNumber']
	newResponseComputer.model=computerDict['Model']
	newResponseComputer.name = computerDict['Name']
	try:
		newResponseComputer.user = extractValueFromDict(computerDict,'Target_HardwareAssetHasPrimaryUser','DisplayName')
	except:
		#print(newResponseComputer.name+" does not have a primary user in cireson")
		newResponseComputer.user="<None>"

	newResponseComputer.building=computerDict['Building']
	try:
		newResponseComputer.location=extractValueFromDict(computerDict,'Target_HardwareAssetHasLocation','DisplayName')
	except:
		#print(newResponseComputer.name+" does not have a location in cireson")
		newResponseComputer.location="<None>"

	newResponseComputer.locDetail=computerDict['LocationDetails']
	newResponseComputer.room=computerDict['Room']
	try:
		newResponseComputer.status=extractValueFromDict(computerDict,'HardwareAssetStatus','Name')
	except:
		#print(newResponseComputer.name+" does not have a status in cireson")
		newResponseComputer.status="<None>"

	try:
		newResponseComputer.assetType=extractValueFromDict(computerDict,'HardwareAssetType','Name')
	except:
		#print(newResponseComputer.name+" does not have an asset type in cireson")
		newResponseComputer.assetType="<None>"

	newResponseComputer.organization = computerDict['Department']

	return newResponseComputer

#raw response from searchID query, name of the computer in question, session variable to 
#show users more data about duplicate computers

#this is the equivalent of typing in a name in the 'Hardware Asset' field in Cireson
def getSearchID(responseString,computerName,session):
	text=responseString

	#remove excess unnecessary symbols from the list
	text = re.sub('[:,]','',text)
	#Path is always empty, and messes up the order so I can't directly import to 
	#a dictionary, so remove it
	text=text.replace('Path','')
	text=text.replace('}{','')
	text=text.split('"')
	text = list(filter(None,text))

	IdFlag = False
	nameFlag = False

	tempID='dummy'
	tempName='dummy name'

	#iterate through the results and save id and names
	text=text[1:-1]


	#16 is a hardcoded magic number for the length of the searchID response
	#If our search only returned one computer object, return that object's searchID
	if len(text)==16:
		if sys.version_info.major==2:
			computerDict = dict(itertools.izip_longest(*[iter(text)] * 2, fillvalue=""))
		else:
			computerDict = dict(itertools.zip_longest(*[iter(text)] * 2, fillvalue=""))
		#print("success")
		#print("Computer "+computerDict['DisplayName']+" ID = "+computerDict['Id'])
		return computerDict['Id']

	#haven't encountered this yet, but I am assuming will be invalid
	elif len(text)<16:
		print(text[:])
		print("Error, incomplete response from Cireson, returning null search id")
		return('00000000-0000-0000-0000-000000000000')
	
	#if our search returned multiple computers
	elif len(text)>16:
		if settings.verbose:
			print("\nMultiple results returned for computer <"+computerName+">") #put this on a new line to make it look nicer
			print("Double Checking results...")
		nameList=list()
		#make a list of computerName:ID
		for x in text:
			if 'Id' == x:
				IdFlag = True
			elif 'DisplayName' == x:
				nameFlag = True
			elif IdFlag is True:
				tempID = x
				IdFlag = False
			elif nameFlag is True:
				tempName =x
				nameFlag = False
			elif tempID != 'dummy' and tempName != 'dummy name':
				nameList.append(tempName)
				nameList.append(tempID)
				tempID='dummy'
				tempName='dummy name'


		#create a dictionary consisting of name:searchID for every result
		#and display it to the user
		if sys.version_info.major==2:
			computerDict = dict(itertools.izip_longest(*[iter(nameList)] * 2, fillvalue=""))
		else:
			computerDict = dict(itertools.zip_longest(*[iter(nameList)] * 2, fillvalue=""))
		i=0
		#first check if only one of the returned computers matches names, this happens in 
		#case of computers like "DSS-Mac01" matching with "DSS-Mac010" in the Cireson 
		#autocomplete system
		numMatches=0

		#check both lowercase strings to do a "case-insensitive" comparison
		for key,value in computerDict.items():
			if key.lower() ==computerName.lower():
				numMatches+=1

		if numMatches==0:
			print("No results match the input")
			return('00000000-0000-0000-0000-000000000000')
		#if there was only one match, return it and forget about the rest of the function
		if numMatches==1:
			for key,value in computerDict.items():
				if key == computerName:
					if settings.verbose:
						print("Only one computer matching the name "+computerName+" was found, returning "+computerDict[key])
					return computerDict[key]

		#if there was more than one identical computer that came up in the searchID search...
		print("\nMultiple duplicate entries found, please wait for details to load:")
		#print a list of computer:ID pairs and prompt the user to choose one that they want
		for key,value in computerDict.items():
			#create a placeholder computer to hold values to be presented to the user
			hardwareURL='https://service.REDACTED.asu.edu/AssetManagement/HardwareAsset/Edit/'+value
			hardwarePage = session.get(hardwareURL)
			summaryComputer = parseCiresonHardwareResponse(hardwarePage.text)
			print(str(i)+"- Name: "+key+" ID: "+value)
			print("\tUser:"+summaryComputer.user+", PCN: "+str(summaryComputer.PCN)+", Serial: "+summaryComputer.serial+", Building: "+summaryComputer.building+", Room: "+summaryComputer.room)
			i+=1
		choice=input("Please make selection based on list position # ('s' if you wish to skip):")
		if choice is 's':
			return '00000000-0000-0000-0000-000000000000'
		validInput=False
		while validInput==False:
			try:
				if 0<= int(choice) <i:
					validInput=True
					i=0
					for key,value in computerDict.items():
						if i==int(choice):
							print("Returning-- Computer "+key+" ID = "+value)
							return value
						else:
							i+=1
				else:
					print("Error, input out of bounds")
					choice=input("Please try again: ")
			except:
				print("Error, input not a number")
				choice=input("Please try again: ")

'''
	print('PCN= '+computerDict['AssetTag'])
	print('serial= '+computerDict['SerialNumber'])
	print('model= '+computerDict['Model'])
	print('name= '+computerDict['Name'])
	print('user= '+extractValueFromDict(computerDict,'Target_HardwareAssetHasPrimaryUser','DisplayName'))
	print('building= '+computerDict['Building'])
	print('location= '+extractValueFromDict(computerDict,'Target_HardwareAssetHasLocation','DisplayName'))
	print('locDetail= '+computerDict['LocationDetails'])
	print('room= '+computerDict['Room'])
	print('status= '+extractValueFromDict(computerDict,'HardwareAssetStatus','Name'))
	print('assetType= '+extractValueFromDict(computerDict,'HardwareAssetType','Name'))
	print('organization = '+computerDict['Department'])
	print('Serial Number= '+computerDict['SerialNumber'])

	return newResponseComputer
	'''
#end of function
#This function adds the search ID variables from a light Cireson search
#to a list of computer objects so that we can do a full Cireson search
def addDictToList(computerDict,computerList):
	for computer in computerList:
		#if we find a match via names
		if computer.name in computerDict.keys():
			print(computer.name+" was found in the dictionary with search id:"+
				computerDict[computer.name])
			#add the id to the obj
			computer.searchID = computerDict[computer.name]
		else:
			print(computer.name+" was not found in the dictionary")

#singluar version of the above function
def addIDFromDict(computer,computerDict):
	if computer.name in computerDict.keys():
		print(computer.name+" was found in the dictionary with search id:"+
			computerDict[computer.name])
		#add the id to the obj
		computer.searchID = computerDict[computer.name]
	else:
		print("Error, response was not empty, but "+computer.name+" was not found in Cireson")
