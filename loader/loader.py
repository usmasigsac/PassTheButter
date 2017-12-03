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

def newProc(f):
    def wrapper(*args, **kwargs):
        p = mp.Process(target=f, args=args, kwargs=kwargs)
        p.start()
    return wrapper

class Job:
  def __init__(self,name,loader):
    self.path = name
    self.name = name.split('/')[2]
    self.payload = importlib.import_module('loader.pool.test2.pwn')#importlib.util.spec_from_file_location("pwn",self.path)
    self.threads = {}
    self.stations = [] #managed by launcher
    self.interval = 1
    self.enabled = False
    self.lastRun = 0
    self.flags = {}
    self.service = ''
    #self.service = getattr(self.payload,"SERVICE")

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
      self.disable()
      loader.jobs.remove(self.name)
    except:
      print("[#] Error stopping %s"%self.name)

  def newFlags(self,job_id,flags,service):#hook
    pass

  def run(self):
    try:
      print(hasattr(self.payload, 'pwn'))
      if hasattr(self.payload, 'pwn'):
        for ip in self.stations:
          print("[#] Running...")
          flag = getattr(self.payload,'pwn')(ip) #user inputs a function 'pwn' that returns the flag
          self.flags[ip] = flag
          print(flag)
        self.newFlags(self.name,self.flags,self.service)
    except Exception as e:
      print("[!!] Error during %s runtime"%self.name)
      print(str(e))

class Pool:
  def __init__(self,pooldir,loader):
    self.location = pooldir
    self.loader = loader

  def get(self):
    return subprocess.getoutput(['ls '+self.location+'/']).split('\n')
  
  def check(self):
    diff = []
    for file in self.get():
      if file not in self.loader.loaded and "pycache" not in file and "init" not in file:
        diff.insert(0,file)
    return diff

class Loader:
  def __init__(self,pooldir,config_file='test.cfg',log_file='loader.log'):
    self.pool = Pool(pooldir,self)
    self.pooldir = pooldir
    self.load = self.pool.get
    self.loaded = []
    self.jobs = []
    self.config = config_file
    self.log = open(log_file,'w')
    self.enabled = False
    self.exitstatus = 0
    self.payload_path = ""

  def exception(self,exception,location):
    print("[!!] %s during %s" % (exception,location))

  def requirements(self,env,dir):
    #NOTE: the name of the .txt is the install env to be used.
    #For example, if you needed pwntools, you would simply
    #put 'pwntools' on it's own line in pip.txt.
    #The 'env' parameter specifies which install environment
    #to use.
    reqs_f = open((dir+'/%s.req' % env),'r')
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
        self.exception(sys.exc_info()[0],"requirements installation")
        err = "[!!] Ignoring %s"%req
        print(err)
        self.log.write(err)
        continue
    #print("[#] Requirements installed.")

  def newjobs(self,boolean,jobs):#hook
    pass

  def checkfile(self):
    pass

  def kill(self):
      exit(0)

  @async
  def run(self):
    try:
      while self.enabled:
        new = self.pool.check()
        if new != []:
          for newfile in new:
            os.system('unzip -qq -u '+self.pooldir+newfile+" -d "+self.pooldir)
            #name of zip, folder, and payload
            file = newfile.split('.zip')[0]
            newdir = self.pooldir+file
            os.system('touch '+newdir+"/__init__.py")
            env = subprocess.getoutput('ls '+newdir+'/*.req').split('.req')[0]
            env = env.split(newdir+"/")[1]
            self.requirements(env,newdir) #install new requirements

            #new thread in case installing takes a bit
            try:
              if env == 'pip':
                #@async
                py_compile.compile('%s.py' % (newdir+"/"+file))
                os.system('cp '+newdir+'/__pycache__/'+file+".cpython-34.pyc "+newdir+"/pwn.pyc")
              else:
                #@async
                os.system('gcc -o %s %s.c' % (newdir+file,newdir+file))
            except KeyboardInterrupt:
              self.log.write("[#] Exited on Ctrl-C")
              exit(0)             
            except:
              self.exception(sys.exc_info()[0],"on %s's installation" % file)
              print("[!!] %s not compiled." % file)
              continue

            #init job
            if file not in self.loaded:
                self.loaded.insert(0, file)
                newjob = Job(newdir + "/pwn.pyc", self)
                self.jobs.insert(0,newjob)
                print("[#] Job < %s > added." % file)
                self.log.write("[#] New jobs created.")
                self.newjobs(True,[newjob])

    except KeyboardInterrupt:
      self.log.write("[#] Exited on Ctrl-C")
      exit(0)
    # except:
    #   self.log.write("[!!] %s at %s" % (sys.exc_info()[0],time.time()))
    #   wait = True
    #   while wait:
    #     inp = input('> ')
    #     if inp[0] == "r":
    #       self.run()
    #       wait = False
    #     elif inp[0] == "p":
    #       print(sys.exc_info())
    #       wait = False
    #     elif inp[0] == "e":
    #       wait = False
    #     else:
    #       print("[#] Please reboot or continue.")

if __name__ == "__main__":
#  try:
    loader = Loader("pool/",sys.argv[1],sys.argv[2])
    loader.run()
  # except:
  #   if len(sys.argv) != 3:
  #     print("[#] Usage: loader.py <config.cfg> <loader.log>")
    # else:
    #   print("[!!] Error:")
    #   print(sys.exc_info())
