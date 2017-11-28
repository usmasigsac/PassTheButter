#!/usr/bin/evn python

#PURPOSE: The loader installs any requirements deemed necessary by the team,
#as well as compiles the .py and .c files provided by the user. The .pyc and 
#binaries are then sent to the launcher, which executes them.

#check requirements.txt for updates

#QUEUE:build a priority queue of file objects (file descriptors)
	#priority 0: not yet loaded
	#priority 1: already loaded

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