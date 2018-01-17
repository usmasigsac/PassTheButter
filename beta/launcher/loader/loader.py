#! /usr/bin/env python3

import os
import sys
import importlib
import subprocess
import py_compile
from threading import Thread
from .jobs import Job

def newThread(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

class Pool:
    def __init__(self, pooldir, loader):
        self.location = pooldir
        self.loader = loader

    def get(self):
        return subprocess.getoutput(['ls ' + self.location + '/']).split('\n')

    def check(self):
        diff = []
        for file in self.get():
            if file not in self.loader.loaded and 'pycache' not in file and 'init' not in file:
                diff.insert(0, file)
        return diff


class Loader:

    def __init__(self, exploit_dir):
        self.pool = Pool(exploit_dir, self)
        self.pooldir = exploit_dir
        self.load = self.pool.get
        self.loaded = []
        self.jobs = []
        self.enabled = False
        
        # idek
        self.payload_path = ''

    def newJobs(self, val:bool, jobs:list(Job) ):
        pass

    @newThread
    def run(self):
        try:
            while self.enabled:
                new = self.pool.check()
                if new:
                    for file in new:
                        os.system('unzip -qq -u' + self.pooldir + file + ' -d ' + self.pooldir)
                        file = file.split('.zip')[0]
                        newdir = self.pooldir + file
                        os.system('touch ' + newdir + '/__init__.py')
                        
                        # env = subprocess.getoutput('ls ' + newdir + '/*.req')
                        # env = env.split(newdir + '/')[1]
                        # self.requirements(env, newdir)

                        try:
                            py_compile.compile('%s.py' % newdir + '/' + file)
                            os.system('cp ' + newdir + '/__pycache__/' + file + '.cpython-34.pyc ' + newdir + '/pwn.pyc')
                        except Exception as e:
                            print(e)
                            sys.exit(0)
                        
                        if file not in self.loaded:
                            self.loaded.insert(0, file)
                            newjob = Job(newdir + '/pwn.pyc', self)
                            self.jobs.insert(0, newjob)
                            print('[+] Job %s added' % file)
                            self.newJobs(True, [newjob])

        except Exception as e:
            print('lol fail')
            print(e)
        

if __name__ == '__main__':
    try:
        ldr = Loader('../../exploits')
        ldr.run()
    
    except:
        if len(sys.argv) != 3:
            print('[-] Usage: loader.py <relative exploit_dir path>')
        else:
            print('epic fail')
            print(sys.exc_info())