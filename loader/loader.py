#!/usr/bin/evn python3

#PURPOSE: The loader installs any requirements deemed necessary by the team,
#as well as compiles the .py and .c files provided by the user. The .pyc and
#binaries are then sent to the launcher, which executes them.

###IMPORTS###
import sys
import os
import subprocess
#############


def exceptionHandler(exception):
	???


class loader:
	#used to check requirements.txt for updates.
	#NOTE: the name of the .txt is the install env to be used.
	#For example, if you needed pwntools, you would simply
	#put 'pwntools' on it's own line in pip.txt.
	#The 'env' parameter specifies which install environment
	#to use.
	def check_req(env):
		#use which to find if it exists
		reqs_f = open(('%s.txt' % env),'r')
		reqs = []
		for line in reqs_f:
			if '/' not in subprocess.check_output(['which',line.strip()]):
				reqs.insert(0,line.strip()) #reqs is mutable, no need to reassign
				print("[#] Added %s to install queue..." % line.strip())
			else:
				pass
		try:
			if env == "pip":
				install = "pip install " + ' '.join(x for x in reqs)
				os.system(install)
			else:
				install = env+" install " + ' '.join(x for x in reqs)
				os.system(install)
			print("[#] Requirements installed.")
		except:
			exceptionHandler(exception)

	#QUEUE:build a priority queue of file objects (file descriptors)
		#priority 0: not yet loaded
		#priority 1: already loaded
		#FORMAT: (PRIORITY, VALUE)
	fileQueue = []

	def buildQueue(fileQueue):
		#fileQueue in this case will not be the global one, since
		#'global fileQueue' is not declared in this function. It
		# will only be modifying it's input and returning that queue.

	def run:
		global fileQueue
		#try:
			#loop:
				#if 0 == curr.head.priority:
					#curr = queue.head
				#compile curr
					#if curr is a dir, compile each .py, .c
				#package curr in tar ball, zip it
				#send curr.tar.gz to launcher
				#set priority = 1
			#end loop


		#except:
			#log error
			#if non-critical, restart looper
			#else, push notification to admin

if __name__ == "__main__":
	loader.run()