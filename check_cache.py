#! /usr/bin/python
#subprocess to be called on every invocation of the cireson command (if not already present)
#that deletes the cached user login and password + any cached computers

import os
import sys
import atexit
import time
import signal
import pickle


pid=str(os.getpid())

pidfile='delete_cache.running'
userfile='user.cache'

def cleanup():
	os.remove(pidfile)
	os.remove(userfile)
atexit.register(cleanup)

#if user enters another command while the caches are still alive, kill the old process and 
#create a new timer process
if os.path.isfile(pidfile):
	file=open(pidfile,'r')
	lines=list()
	for line in file:
		lines.append(line)
	file.close()

	#backup user data 
	file=open(userfile,'rb')
	if sys.version_info.major == 2:
		current_session=pickle.load(file)
	file.close()

	process_to_kill=lines[1]
	#print('killing process:{}'.format(process_to_kill))
	try:
		os.kill(int(process_to_kill),signal.SIGTERM)
	except OSError:
		1+1 #there was no process to kill

	#backup all cache info and wait for exit
	open(pidfile,'w').write('Details valid until:{}\n'.format(str(int(time.time())+900)))
	open(pidfile,'a').write(format(pid))
	file=open(userfile,'wb+')
	pickle.dump(current_session,file,protocol=2)
	file.close()
	time.sleep(900)#15 minutes
	#time.sleep(15)
else:
	#first line is the time until which the user login credentials are valid
	#second line is the pid of the currently running check_cache process
	open(pidfile,'w').write('Details valid until:{}\n'.format(str(int(time.time())+900)))
	open(pidfile,'a').write(format(pid))
	#time in seconds I want user to manually enter credentials/check back for updates
	time.sleep(900) #15 minutes
	#time.sleep(15)
	#if os.path.isfile('user.cache'):
		#os.remove('user.cache')