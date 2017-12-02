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
import importlib
import multiprocessing as mp
#############

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

class Job:
    def __init__(self,name,loader):
        self.name = name
        self.payload = importlib.abc.SourceLoader(self.name)
        self.path = name + '/'
        self.threads = {}
        self.stations = [] #managed by launcher
        self.interval = 0
        self.enabled = False
        self.lastRun = 0
        self.flags = []

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

    def writeLog(self,string):
        loader.log.write("[#] %s"%string)

    def enable(self):
        self.enabled = True

    def disable(self):
    	self.enabled = False

    def changeStations(self,newstations):
        self.stations = newstations

    def changeInterval(self,newinterval):
        self.interval = newinterval

    def stop(self):
    	try:
        	loader.jobs.remove(self.name)
        except:
        	print("[#] Error stopping %s"%self.name)

    def newFlags(self,job_id,flags):#hook
    	pass

    def run(self):
    	try:
	        if hasattr(self.payload, 'pwn'):
	            for team in self.stations:
	                flag = getattr(self.payload,'pwn')(team) #user inputs a function 'pwn' that returns the flag
	                self.flags.insert(0,flag)
	                self.newFlags(self.name,self.flags)
	    except:
	    	print("[!!] Error during %s runtime"%self.name)

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

	def exception(self,exception,location):
		print("[!!] %s during %s" % (exception,location))

	def requirements(self,env,dir):
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
		for req in reqs:
			try:
				os.system(env+" install " +req)
				print("[#] Installing requirement %s..."%req)
			except KeyboardInterrupt:
				self.log.write("[#] Exited on Ctrl-C")
				exit(0)
			except:
				exception(sys.exc_info()[0],"requirements installation")
				err = "[!!] Ignoring %s"%req
				print(err)
				self.log.write(err)
				continue
		print("[#] Requirements installed.")

	def newjobs(self,boolean,jobs):#hook
		pass

	def checkfile(self):
		pass

	def run(self):
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
						try:
							if env == 'pip':
								@async
								py_compile.compile('%s.py' % newdir)
							else:
								@async
								os.system('gcc -o %s %s.c' % (newdir,newdir))

						except KeyboardInterrupt:
							self.log.write("[#] Exited on Ctrl-C")
							exit(0)							
						except:
							exception(sys.exc_info()[0],"on %s's installation" % newdir)
							print("[!!] %s not compiled." % newdir)
							continue

						#init job
						newjob = Job(newdir,self)
						self.jobs.insert(0,newjob)
					self.log.write("[#] New jobs created.")
					self.newjobs(True,self.jobs)

		except KeyboardInterrupt:
			self.log.write("[#] Exited on Ctrl-C")
			exit(0)
		except:
			self.log.write("[!!] %s at %s" % (sys.exc_info()[0],time.time()))
			wait = True
			while wait:
				input = input('> ')
				if input[0] == "r":
					self.run()
					wait = False
				elif input[0] == "c":
					wait = False
				else:
					print("[#] Please reboot or continue.")
					sleep(1)

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("[#] Usage: loader.py <config.cfg> <loader.log>")
	loader = Loader("pool/",pid,sys.argv[1],sys.argv[2])
	loader.run()