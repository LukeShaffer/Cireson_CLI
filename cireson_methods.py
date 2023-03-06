#This file contains the actual work done by all the functions used in my command-line 
#utility "cireson.py"

import requests
import sys
from requests_ntlm import HttpNtlmAuth
from ciresonResponseParser import getSearchID
from ciresonResponseParser import parseCiresonHardwareResponse
import settings
from settings import computerObj


#class to store persistant variables so I don't have to pass a million things to my functions
class session_details:
	ID='uuid-here'
	fullName='test-name'
	session=None
	verbose=False

#for identifying which aspects of a computer in Cireson are incomplete
def bits(n):
	while n:
		b=n&(~n+1)
		yield b
		n^=b

#prints error information about missing fields of a comptuer retrieved from cireson
def print_errors(computer,flags):
	if flags !=0:
		print('Computer <{}> has a...'.format(computer.name))
		for b in bits(flags):
			if b==1:
				print('\tmodel error')
			if b==2:
				print('\tserial error')
			if b==4:
				print('\tpcn error')
			if b==8:
				print('\tstatus error')
			if b==16:
				print('\ttype error')
			if b==32:
				print('\tname error')
			if b==64:
				print('\tlocation detail error')
			if b==128:
				print('\torganization error')
			if b==256:
				print('\tuser error')
	else:
		return


def cireson_connect(verbose):
	from getpass import getpass
	session = requests.Session()
	connected = False
	while connected == False:
		if sys.version_info.major==2:
			username=raw_input("Please enter your asu username: ")
		else:
			username = input("Please enter your asu username: ")
		ASUpass=getpass(prompt="Please enter your password: ")
		if verbose:
			print("Connecting to service.REDACTED.asu.edu....")
		session.auth = HttpNtlmAuth(username,ASUpass)
		r = session.get('http://service.REDACTED.asu.edu')
		if r.status_code == 401:
			print("Error, invalid login info, try again")
		elif r.status_code == 200:
			connected = True
	#save the user session information returned so that I can parse the userId
	#and dynamically add it to my query url below
	bigText = r.text.split('user: {')
	#get rid of everything before "var session"
	bigText = bigText[1]
	bigText = bigText.split('"')

	'''
	debug, find new values on the user's id
	for x in range(60):
		print(str(x)+": "+bigText[x])
	'''

	IDString = bigText[3]
	fullName = bigText[7]
	position = bigText[29]

	current_session=session_details()
	current_session.ID=IDString
	current_session.fullName=fullName
	current_session.session=session
	current_session.verbose=verbose

	if verbose:
		print("Now logged in to http://service.REDACTED.asu.edu")
		print("Welcome, "+fullName+": "+position)
	return current_session

#returns a computerObj from an input name, or None if there was an issue
def lookup_by_name(current_session,computerName):
	#magic values from the js
	session=current_session.session

	baseQueryURL= 'https://service.REDACTED.asu.edu/REDACTED'
	userId= current_session.ID
	isUserScoped='false'
	objectClassId='########-####-####-####-############'

	searchFilter = computerName #the search keyword
	searchPayload = {'userId': userId, 'isUserScoped': isUserScoped, 'objectClassId': objectClassId, 'searchFilter': searchFilter}
	

	search = current_session.session.get(baseQueryURL, params=searchPayload)
	
	#error checking

	#if we get an empty response, print error to user and return None
	if len(search.text) < 5:
		return None
	else:
		computer=computerObj()
		#find the search ID of each computer
		if settings.verbose:
			sys.stdout.write("Obtaining searchID of computer: {}...".format(computerName))
		computer.searchID = getSearchID(search.text,computerName,session)
	
	#now fill out the rest of the computer's details
	baseHardwareURL = 'https://service.REDACTED.asu.edu/REDACTED'
	flags=0 #bit flags for each aspect of a cireson computer that could be missing

	#pull asset details from Cireson
	hardwareURL = baseHardwareURL+computer.searchID
	hardwarePage = session.get(hardwareURL)
	newComputer = parseCiresonHardwareResponse(hardwarePage.text)
	#if any fields are not present in cireson, this method^ will set them to '<None>'

	if newComputer ==None:
		return None
	flags = newComputer.isComplete()
	if current_session.verbose:
		if flags!= 0:
			print("Computer "+newComputer.name+" is not complete")
			print_errors(newComputer,flags)

		else:
			print("Computer "+newComputer.name+" is complete\n")
		
	return newComputer #if we got this far, there is a computer object to return, so just return it 

def printSummary(computerList,args):
	print("Query Summary:\n")
	for i,computer in enumerate(computerList):
		if args.name is not None:
			print(args.name[i]+": ")

		if args.getUser:
			1+1
















