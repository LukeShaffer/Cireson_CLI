#! /usr/bin/python


'''
Installation instructions: 


for windows users, make sure you have either python 2 or 3 installed, as well as the requests and requests_ntlm modules 
installed

mac users will need to install pip and from there, the requests module:

sudo easy_install pip

pip install requests
pip install requests_ntlm <- this is necessary to be able to log in to the cireson server
pip install tqdm

in case I forget to remove all the carriage returns, run this command on a mac:
tr -d '\r' < name_of_file > name_of_new_file(must be different to avoid side effects)

'''

'''
text description of what I want this file to do

full-on command line automation of all the tedious cireson lookups/checks/imaging verification

the goal is for a user .

example use cases:
python cireson --getUser -name REDACTED-<PCN>

python cireson --setUser -name REDACTED-<PCN> -newName

python cireson --getDetails
				--setDetails -imaged -initials <initials to use>
				--isComplete
				--getModel
				--getPCN
				--getName
				--verify //checks for common errors, missing fields, etc, and prints a list


'''

'''
TODO
Implement computer caching mechanism
Add option to force online lookups if other people are concurrently mucking with computer details


'''

#first search the cache file for the computer
#the cache file will save computers in the form 
import sys
import os
import pickle
import argparse
import subprocess
from tqdm import tqdm #progress bars!!


import cireson_methods
import settings
from settings import computerObj
from cireson_methods import session_details

parser=argparse.ArgumentParser(description="All-in-one Cireson computer checker."+  
	"Examine details of any computer and (soon) be able to change them on the fly "+
	"just as easily\n"+

	"This program consists of actions (specified with -- before their names) and identifiers (things like name and PCN)")
#positional parameter howto-> parser.add_argument("path",help="Path of the file to be checked")
parser.add_argument("-v","--verbose",help="Print all error messages as they occur"
	,action="store_true")


#Actions section
parser.add_argument("--getUser",help='Return the name of the primary user of the specified computer',action='store_true')
#parser.add_argument("--setUser",help='Set the name of the primary user of the specified computer',
#	action='store',nargs='*')

parser.add_argument("--getDetails",help='Return a list of deployment details of the specified computer',action='store_true')

parser.add_argument("--getSerial",help='Return the serial number of the specified computer',action='store_true')

parser.add_argument("--getModel",help='Return the model name of the specified computer',action='store_true')

parser.add_argument("--getName",help='Return the name of the specified computer',action='store_true')

parser.add_argument("--getPCN",help='Return the PCN of the specified computer',action='store_true')

parser.add_argument("--getLocation",help='Return the location of the specified computer',action='store_true')

parser.add_argument("--getOrg",help='Return the organization of the specified computer',action='store_true')

parser.add_argument("--createReport",help='flags the program to produce uniform output of the form <computer> : <user : location : room : organization : serial>',action='store_true')

parser.add_argument("--toFile",help='flags the program to redirect output to a file, overwriting if it already exists',action='store',dest='toFile',default=None)



parser.add_argument('-c','-computer',help='Name or pcn of computer(s) to look up (space separated, can be a combination of both)',action='store',nargs='*',dest='computer',default=None)

args=parser.parse_args()

#print(args.name)
if args.verbose:
	settings.verbose=True

#if a cleanup process is already running, then we have saved user credentials and maybe a 
#list of previously looked-up computers
if os.path.isfile('delete_cache.running'):
	with open('user.cache','rb') as file:
		current_session=pickle.load(file)



#if this is a fresh session, create the cache file and start
else:
	current_session = cireson_methods.cireson_connect(args.verbose)
	with open('user.cache','wb+') as file:
		#protocol must remain 2 to keep compatibility with mac python 2
		pickle.dump(current_session,file,protocol=2)

#either re-up the cache_deletion process if already running or just create it if not

#if windows, will be running python3, which supports DETACHED_PROCESS
if os.name=='nt':
	subprocess.Popen(['python','check_cache.py'],creationflags=subprocess.DETACHED_PROCESS) #refresh login timer
#if mac, will be running python2 by default
else:
	subprocess.Popen(['python','check_cache.py']).pid

#this must be here after the prompt for the username, or it will be written to file as well
if args.toFile is not None:
	#I should put some kind of sanitation check here, this is dangerous
	sys.stdout=open(args.toFile,'w')


queryComp=computerObj()

#create title for collumns if creating a report
if args.createReport:
	print('Format:\ncomputer       : user                     : location            : room   : organization        : serial')

#display results for all computers
if args.computer is not None:

	#only display progress bar if more than one computer is entered
	if len(args.computer)==1:
		input_computer_list=args.computer
	else:
		input_computer_list=tqdm(args.computer)


	for input_computer in input_computer_list:

		queryComp=cireson_methods.lookup_by_name(current_session,input_computer)
		
		#will only be None when the searchID query does not fish anything up-hence, no computer details at all
		if queryComp is not None:

			#This must come first because it is the only option to justify a continue and thus be separate to prevent 
			#other switch cases from executing
			if args.createReport:
				print('{computer:1s}: {user:25s}: {location:20s}: {room:7s}: {organization:32s}: {serial}'.format(computer=queryComp.name,user=queryComp.user,
															location=queryComp.location,room=queryComp.room, organization=queryComp.organization,serial=queryComp.serial))
				continue
			if args.getUser:
				print(queryComp.name+": "+queryComp.user)

			if args.getDetails:
				print(queryComp.name+" details:")
				queryComp.printDetails()

			if args.getSerial:
				1+1
			if args.getModel:
				1+1
			if args.getName:
				1+1
			if args.getPCN:
				print(queryComp.name+": "+queryComp.PCN)

			if args.getLocation:
				print(queryComp.name+": "+queryComp.location)
			if args.getOrg:
				print(queryComp.name+": "+queryComp.organization)

		#if the computer did not come up in the cireson search box
		else:
			if args.createReport:
				print('{name}: DNE in Cireson'.format(name=input_computer))
			else:
				print("Error, cannot find computer <{name}> in Cireson".format(name=input_computer))


































