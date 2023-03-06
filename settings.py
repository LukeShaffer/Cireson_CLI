#settings for global python variables, and the computerObj class
global verbose
verbose = False
class computerObj:
	searchID = '00000000-0000-0000-0000-000000000000'#the id given by the xml lookup is cated directly to https://service.REDACTED.asu.edu/AssetManagement/HardwareAsset/Edit/
	PCN=0000000
	serial='dummy serial'
	model='dummy model'
	name = 'dummy name'
	user = 'dummy user'
	building='dummy building'
	location='dummy location (building)'
	locDetail='dummy location details (room)'
	room='dummy room'
	status='dummy status'
	assetType='dummy type'
	organization = 'dummy organization'


	def __init__(self):
		searchID = '00000000-0000-0000-0000-000000000000'#the id given by the xml lookup is cated directly to https://service.REDACTED.asu.edu/AssetManagement/HardwareAsset/Edit/
		PCN=0000000
		serial='dummy serial'
		model='dummy model'
		name = 'dummy name'
		user = 'dummy user'
		building='dummy building'
		location='dummy location (building)'
		locDetail='dummy location details (room)'
		room='dummy room'
		status='dummy status'
		assetType='dummy type'
		organization = 'dummy organization'

	def toString(self):
		return str(self.model+' '+self.serial+' '+str(self.PCN)+' '+self.status
			+' ' +self.assetType+' '+self.name+' '+self.locDetail+' '+
			self.organization+' '+self.user)
	def toStringID(self):
		return str(self.name+': '+self.searchID)
	def printDetails(self):
		#print(self.__dict__)
		print('PCN= '+str(self.PCN))
		print('serial= '+self.serial)
		print('model= '+self.model)
		print('name= '+self.name)
		print('user= '+ self.user)
		print('building= '+self.building)
		print('location= '+self.location)
		print('locDetail= '+self.locDetail)
		print('room= '+self.room)
		print('status= '+self.status)
		print('assetType= '+self.assetType)
		print('organization = '+self.organization)
#function checks if all the attributes of the computer are valid, returning a 0 if
#the computer is "complete" (has no empty entries), and various binary values corresponding
#to the errors encountered
	def isComplete(self):

		statusTypes =('Ordered','Received','In Stock','On Hold',
			'Repurpose Inventory','Repair, Test, Etc.','Salvage Inventory',
			'Deployed','Primary','Secondary','TA / FA','Computing Lab', 
			'Teaching Station','Signage','Offsite','Server','Other','Virtual Machine',
			'Student Worker','Departmental','Loaned','Retired','Lost/Stolen','Disposed')

		assetTypes = ('Computer','Virtual Machine','Tablet','Computer Peripheral','Printer','Scanner',
			'Monitor','Touch Display','Projector','Camera','Digital Lab Equipment',
			'A/V Loan Equipment','Point-of-Sale Equipment','Networking Equipment')

		#define bit flags


		#Return values (bin):
		#000 000 000		fine
		#000 000 001		model error
		#000 000 010		serial error
		#000 000 100		pcn error
		#000 001 000		status error
		#000 010 000		type error
		#000 100 000		name error
		#001 000 000		location details error
		#010 000 000		organization error
		#100 000 000		user error
		modelError= int('000000001',2)
		serialError=int('000000010',2)
		pcnError=   int('000000100',2)
		statusError=int('000001000',2)
		typeError=  int('000010000',2)
		nameError=  int('000100000',2)
		locDetError=int('001000000',2)
		orgError=   int('010000000',2)
		userError=  int('100000000',2)


		flags =     int('000000000',2)
		#model
		if self.model == '' or self.model == '<None>' or self.model =='dummy model':
			self.model = '<None>'
			flags|=modelError
			#if settings.verbose:
				#print('\nModel ERROR on line: '+str(count)+ ' Read Status: ' +parts[0]+'\n')

		#serial
		if self.serial =='dummy serial':
			flags|=serialError

		if len(self.serial)<7:
			flags|=serialError
			if self.serial == '' or self.serial == '<None>':
				self.serial = '<None>'
#			if settings.verbose:
#				print('\nSerial ERROR on line: '+str(count)+ ' Read Serial: ' +parts[1]+'\n')

		#PCN
		if self.PCN == '' or self.PCN == '<None>' or self.PCN =='0000000':
			flags|=pcnError
			self.PCN = '<None>'
#			if settings.verbose:
#				print('\nPCN ERROR on line: '+str(count)+ ' Read PCN: ' +parts[2]+'\n')
		#second test to test if PCN is a number or invalid
		try:
   			val = int(self.PCN)

		except ValueError:
			flags|=pcnError
#			if settings.verbose:
#				print('\nPCN ERROR on line: '+str(count)+ ' Read PCN: ' +parts[2]+'\n')
		
		#status
		if self.status == '' or self.status == '<None>' or self.status=='dummy status':
			flags|=statusError
			self.status = '<None>'

		if self.status in statusTypes: #read status is valid
			1+1
		else:
			flags|=statusError

#			if settings.verbose:
#				print('\nSTATUS ERROR on line: '+str(count)+ ' Read Status: ' +parts[3]+'\n')
		#type
		if self.assetType in assetTypes: #read asset type is valid
			1+1
		else:
			flags|=typeError
#			if settings.verbose:
#				print('\nTYPE ERROR on line: '+str(count)+ ' Read type: ' +parts[4]+'\n')
		#name
		if len(self.name) <3:	#arbitrary length requirement
			if self.name == '':
				self.name = '<None>'
			flags|=nameError
		if self.name == '<None>' or self.name =='dummy name':
			flags|=nameError
#			if settings.verbose:
#				print('\nNAME ERROR on line: '+str(count)+ ' Read name: ' +parts[5]+'\n')
		#location details
		if self.locDetail == '' or self.locDetail == '<None>' or self.locDetail =='dummy location details (room)':
			self.locDetail = '<None>'
			flags|=locDetError
#			if settings.verbose:
#				print('\nLOCATION DETAIL ERROR on line: '+str(count)+ ' Read location detail: ' +parts[6]+'\n')
		#organization
		if self.organization == '' or self.organization == '<None>' or self.organization=='dummy organization':
			self.organization = '<None>'
			flags|=orgError
#			if settings.verbose:
#				print('\nORGANIZATION ERROR on line: '+str(count)+ ' Read organization: ' +parts[7]+'\n')
		#user
		if self.user == '' or self.user == '<None>' or self.user=='dummy user':
			self.user = '<None>'
			flags|=userError
#			if settings.verbose:
#				print('\nUSER ERROR on line: '+str(count)+ ' Read user: ' +parts[8]+'\n')

		#The world is not yet ready for this much cleanup
		if 'local_users' in self.user:
			flags|=userError
#			if settings.verbose:
#				print('\nUSER ERROR on line: '+str(count)+ ' Read user: ' +parts[8]+'\n')
		return flags



#returns 0 if no common errors, or sets a flag bit depending on the type of error
	def checkCommonErrors(self):
		flags=int('00',2)
		if self.building != self.location:
			print(computer.name+"'s location and building do not match")
			flags=flags|int('01',2)
		if self.room != self.locDetail:
			print(computer.name+"'s room and location detail do not match")
			flags=flags|int('10',2)

		return flags
