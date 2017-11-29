#!/usr/bin/evn python3

#PURPOSE: The loader installs any requirements deemed necessary by the team,
#as well as compiles the .py and .c files provided by the user. The .pyc and
#binaries are then sent to the launcher, which executes them.

###IMPORTS###
import sys
import os
import subprocess
from threading import Thread
import py_compile
import time
#############

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

class Job:
    def __init__(self,name):
        self.name = name
        self.path = name + '/'
        self.threads = {}
        self.stations = []
        self.interval = 0
        self.enabled = False
        self.lastRun = 0

    def load(self):
        """
        loads from backup

        :return:
        """
        pass

    def export(self):
        """
        writes to backup

        :return:
        """
        pass

    def writeLog(self):
        pass

    def enable(self):
        pass

    def disable(self):
        pass

    def delete(self):
        pass

    def changeStations(self):
        pass

    def changeInterval(self):
        pass

    def beginJob(self):
        pass

    def stopJob(self):
        pass

    def spawnThread(self):
        pass

    def killThread(self):
        pass

    def attack(self):
        return 'Not Initialized'

    def run(self):
        pass

class Pool:
	def __init__(self,pooldir,loader):
		self.location = pooldir
		self.loader = loader

	def get():
		return subprocess.getoutput(['ls'+self.location]).split('\n')
	
	def check():
		diff = []
		for file in self.get():
			if file not in self.loader.loaded:
				diff.insert(0,file)
		return diff

class Loader:
	def __init__(self,pooldir,config_file,log_file):
		print("[#] Initializing ...")
		self.pool = Pool(pooldir,self)
		self.load = pool.get()
		self.loaded = []
		self.jobs = []
		self.config = config_file
		self.log = open(log_file,'w')
		self.exitstatus = 0

	def exceptionHandler(exception,location,action):
		#use the exception handler to decide what to do in certain situations.
		print("[!!] %s during %s" % (exception,location))
		if action == 1:
			
		elif action == 2:
		elif action == 3:

	def requirements(env,dir):
		#NOTE: the name of the .txt is the install env to be used.
		#For example, if you needed pwntools, you would simply
		#put 'pwntools' on it's own line in pip.txt.
		#The 'env' parameter specifies which install environment
		#to use.
		reqs_f = open((dir+'/%s.txt' % env),'r')
		reqs = []
		for line in reqs_f:
			if '' == subprocess.getoutput('which '+line.strip()):
				reqs.insert(0,line.strip()) #reqs is mutable, no need to reassign
				print("[#] Added %s to install queue..." % line.strip())
		try:
			install = env+" install " + ' '.join(x for x in reqs)
			os.system(install)
			print("[#] Requirements installed.")
		except:
			exceptionHandler(sys.exc_info()[0],"requirements installation",1)

	def run:
		try:
			while True:
				new = self.pool.check()
				if new != []:
					os.system('unzip '+' '.join(newfile for newfile in new))
					for newfile in new:
						#name of zip, folder, and payload
						newdir = newfile.split('.zip')[0]
						env = subprocess.getoutput('ls *.req').split('.req')[0]
						requirements(env,newdir) #install new requirements

						#new thread in case installing takes a bit
						@async
						try:
							if env == 'pip':
								py_compile.compile('%s.py' % newdir)
							else:
								os.system('gcc -o %s %s.c' % (newdir,newdir))
													except:
						except:
							exceptionHandler(sys.exc_info()[0],"on %s's installation" % newdir)
						#init job
						newjob = Job(newdir)
						self.jobs.insert(0,newjob)

		except:
			self.log.write("[!!] %s at %s" % (sys.exc_info()[0],time.time()))
		

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("[#] Usage: loader.py <config.cfg> <loader.log>")
	loader = Loader("pool/",pid,sys.argv[1],sys.argv[2])
	loader.run()