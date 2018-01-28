#!/usr/bin/env python3

import json
import time
import os
import sys
from netaddr import *
from threading import Thread
import gnureadline as readline
#import pyreadline as readline
import re
import requests
import multiprocessing as mp
from loader.loader import Loader

BACKUP_DIR = './backup'
BACKUP_JOBS = BACKUP_DIR + '/jobs'
BACKUP_SERVICES = BACKUP_DIR + '/services'
BACKUP_LAUNCHER = BACKUP_DIR + '/launcher'
BACKUP_CFG_FILE = BACKUP_LAUNCHER + '/cfg'
BACKUP_CONFIG = BACKUP_DIR + '/setup'


def newThread(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.setDaemon(False)
        thr.start()
    return wrapper

def newProc(f):
    def wrapper(*args, **kwargs):
        p = mp.Process(target=f, args=args, kwargs=kwargs)
        p.start()
    return wrapper

######################################################################
""" 
Edit The Following object based on how the competition desires the flags to be submitted
"""
class Scorer:
    def __init__(self,
                 baseUrl='http://127.0.0.1',
                 scorePath='/submit',
                 loginRequired=True,
                 loginFunc=None,
                 loginPath='/login',
                 loginToken={'name':'','value':None},
                 creds={'user':'','pass':''},
                 logger=None,
                 logFile='scoreer.log',
                 backupDir='scorer/',
                 backupFile='scorer.bak',
                 debug=False):
        #self.Pconn, self.Cconn = mp.Pipe()
        self.enabled = True
        self.debug = debug
        self.backupFile = backupFile
        self.backupDir = backupDir
        # this allows for the use of a custom logger beyond the default file used by this class
        self.logFile = logFile
        self.remoteLog = False
        if not logger:
            self.log = self.logger
            self.remoteLog = True
        else:
            self.log = logger

        # This part is used to configure the flag submissions
        # Some competitions require you to logon before initially scoring
        # ex. iCTF has a Login function to use in their API
        # ex. RUCTFe has token authentication and in the past has held a web session
        self.loginRequired = loginRequired
        if loginFunc:
            self.login = loginFunc
            self.session = None
        else:
            self.session = requests.Session()
        self.loginPath = baseUrl + loginPath
        self.scorePath = baseUrl + scorePath
        self.loginToken = loginToken
        self.creds = creds

        # attributes needed for class functionality
        self.flags = []

    def backup(self, dir=None):
        output = dict(
            time=time.strftime('%Y'),
            loginPath=self.loginPath,
            creds=self.creds,
            loginToken=self.loginToken,
            loginRequired=self.loginRequired,
            logFile=self.logFile,
            scorePath=self.scorePath,
            backupFile=self.backupFile,
            backupDir=self.backupDir,
        )
        if self.remoteLog:
            output['logger'] = 'remote logger.'
        outfile = self.backupFile
        if not dir:
            outfile = self.backupDir + time.strftime("%S%M%H%d%m%Y") + outfile
        else:
            outfile = dir + time.strftime("%S%M%H%d%m%Y") + outfile
        try:
            with open(outfile, 'r') as f:
                f.write(json.dumps(output, sort_keys=True))
        except Exception as e:
            print(e)
            return False
        return True


    def logger(self, text, lvl):
        if lvl == 0 and not self.debug:
            return
        LOG_LEVELS = ['DEBUG','INFO','ERROR','FATAL']
        with open(self.logFile, 'r')  as f:
            f.write('[%d]: %s: %s' % (time.time(), LOG_LEVELS[lvl], text))

    def login(self):
        self.log('Attempting to login with creds: %s')
        r = self.session.post(self.loginPath, data=self.creds)
        if r.status_code == 200:
            self.log('Login successful.', 0)
        else:
            self.log('Login fail.', 2)

    @newThread
    def submitFlag(self, payload):
        """

        :param payload: type list: of the format:
                        [string flag, string ip, string jobName, string service
        :return:
        """
        self.log('Submitting flag from Team: %d, Job: %s, Service: %s' % (payload[1], payload[2], payload[3]), 1)
        r = self.session.put(self.scorePath, json={self.loginToken['name']: self.loginToken['value']},data='[%s]' % payload[0])
        if r.status_code == 200:
            self.log('Flag submission on Team: %d, Job: %s, Service: %s. Success!' % (payload[1], payload[2], payload[3]), 0)
        else:
            self.log('Flag submission on Team: %d, Job: %s, Service: %s. Fail!' % (payload[1], payload[2], payload[3]), 2)

    def run(self):
        if self.loginRequired: self.login()

        while self.enabled:
            for flag in self.flags:
                self.log('Received payload: %s' % str(flag), 1)
                self.submitFlag(flag)
            time.sleep(1)

######################################################################

class Launcher:
    #TODO iprange, chaff
    def __init__(self, fname='config.cfg', debug=True):
        self.version = 'v0.1.beta_AF'
        self.DEBUG = debug
        self.cfg = {}
        self.enabled = False
        self.cfgOpts = ['host','iprange','debug','random_chaff','blacklist_targets','whitelist_targets','interval']
        self.randChaff = False
        self.blackList = []
        self.whiteList = []
        self.jobQueue = {}
        self.interval = 5 #*60
        self.attackTypes = ['web','socket']
        self.jobs = {}
        self.hosts = []
        self.services = []
        self.logFile = 'logs/launcher.log'
        self.backupdir = 'backups'
        self.jobsBackupDir = self.backupdir + '/jobs'
        self.cfgBackupDir = self.backupdir + '/cfg'
        self.loaderBackupDir = self.backupdir + '/loader'
        self.scorerBackupDir = self.backupdir + '/scorer'
        self.loaderDir = 'loader/pool/'
        self.remoteLog = False
        self.backupFile = 'launcher.bak'
        self.parseCfg(fname)
        # print(self.cfg.keys())
        # for c in self.cfgOpts:
        #     if c not in self.cfg.keys():
        #         self.log('Incorrect Config File...Make sure all values are present:\n\t%s' % str(self.cfgOpts))
        #         sys.exit(1)

        self.commands = {
            #"add": Command("add", "add a new job", self.createJob, Usage(self.checkFileExists, "job file"),
            #               Usage(self.checkJobNotExists, "job name")),
            "enable": Command("enable", "begin running job", lambda job: job.enable(),
                              Usage(self.checkJobExists, "job name")),
            "disable": Command("disable", "stop running job and kill any threads it is currently running",
                               lambda job: job.disable(), Usage(self.checkJobExists, "job name")),
            "delete": Command("delete", "stop running job, kill any threads it is running, and remove it from launcher",
                              self.deleteJob, Usage(self.checkJobExists, "job name")),
            "list": Command("list", "list all information on current jobs", self.listJobs,
                            Usage(self.checkJobExists, "job name", True)),
            "addjob": Command("addjob", "add and enable newjobs from the queue", self.addJob, Usage(
                    self.inJobQueue, "job name", True)),
            "stations": Command("stations", "change stations that a job will run on",
                                lambda job, stations: job.changeStations(stations),
                                Usage(self.checkJobExists, "job name"),
                                Usage(self.checkIfInts, "stations separated by commas")),
            "interval": Command("interval", "changes the time interval between running the job",
                                lambda job, interval=self.cfg['interval']: job.changeInterval(interval),
                                Usage(self.checkJobExists, "job name"), Usage(
                    lambda i: (True, int(i)) if i.isdigit() and int(i) > 0 else (
                    False, "%s is not a valid interval (number greater than zero)" % i), "interval in seconds")),
            "help": Command("help", "show information from all commands", self.commandHelp,
                            Usage(self.commandExists, "command name", True)),
            #"quit": Command("quit", "kill all jobs and exit out of launcher", self.quitLauncher),
            "print": Command("print", "print most recent lines from the log file",
                             lambda job, lines=10: job.printLog(lines), Usage(self.checkJobExists, "job name"), Usage(
                    lambda i: (True, int(i)) if i.isdigit() and int(i) > 0 else (
                    False, "%s is not a valid number of lines (number greater than zero)" % i), "number of lines",
                    True)),
            #"export": Command("export", "export all jobs to a job file to be imported later", self.exportJobs,
            #                  Usage(lambda i: (True, str(i)), "export location"))
        }
        self.scoreBot = Scorer(logger=self.log, loginRequired=False, loginToken={'name':'X-TEAM-AUTH','value':'2e059bcd-ff85-4142-af4d-906b46840428'})
        self.loader = Loader(self.loaderDir)
        self.loader.newjobs = self.newJobs
        self.loader.enabled = True
        self.loader.run()

    def listJobs(self, job=False):
        if job: print(job)
        else:
            if self.jobs:
                for job in self.jobs.keys():
                    print(job)
            else:
                self.log('No jobs created yet')

    def checkJobExists(self, name):
        if name in self.jobs.keys():
            return (True, name)
        return (False, 'No job named %s' % name)

    def checkJobNotExists(self, name):
        if name not in self.jobs.keys():
            return (True, name)
        return (False, 'Job named %s Already Exists' % name)

    def checkFileExists(self, location):
        # TODO update
        if os.path.isfile(location):
            return (True, location)
        else: return (False, 'No File at location %s' % location)

    def checkIfInts(self, stationList):
        retList = []
        for station in stationList.split(','):
            try:
                retList.append(int(station))
            except ValueError:
                continue
        if retList: return (True, retList)
        return (False, 'Stations but be ints in a comma deliminated list with no spaces')

    def commandExists(self, name):
        if name in self.commands.keys(): return (True, name)
        return (False, 'No command name: %s' % name)

    def commandHelp(self, cmd=False):
        if not cmd:
            self.log('Launcher %s' % self.version)
            self.log('All Commands:')
            for c in self.commands.keys():
                self.log('\t%s -> %s' % (self.commands[c].name, self.commands[c].desc))
                self.log('\t\t' + str(self.commands[c]))
        else:
            self.log('%s -> %s' % (cmd.name, cmd.help))
            self.log('\t' + str(cmd))

    def inJobQueue(self, job):
        if job in self.jobQueue.keys(): return (True, job)
        return (False, 'No job found in queue with name %s' % job)

    def deleteJob(self, jobName):
        self.jobs[jobName].stop()
        del self.jobs[jobName]

    def reboot(self):
        #TODO
        # loadFromBackup()
        pass

    def backup(self):
        #TODO
        # export:
        #       Jobs
        #       cfg
        #       Loader
        output = dict(
            time=time.strftime('%Y'),

        )
        if self.remoteLog:
            output['logger'] = 'remote logger.'
        outfile = self.backupFile
        if not dir:
            outfile = self.backupDir + outfile
        try:
            with open(outfile, 'r') as f:
                f.write(json.dumps(output, sort_keys=True))
        except Exception as e:
            print(e)
            return False
        return True
        pass

    def export(self, cfg=True, jobs=True, loader=True, scorer=True):
        #TODO
        # take in objects to backup

        pass

    def addJob(self, name=False):
        if not name:
            print('Available jobs to add and enable:')
            for jobName in self.jobQueue:
                print(jobName)
                print('\t-'+jobName)
        else:
            job = self.jobQueue[name]
            job.interval = self.interval
            job.enabled = True
            job.newFlags = self.newFlags
            if self.hosts:
                for station in self.hosts:
                    if not self.blackList:
                        job.stations.append(station)
                    elif station not in self.blackList:
                        job.stations.append(station)
            self.jobs[job.name] = job
            del self.jobQueue[job.name]

    def newJobs(self, new, jobs=list()):
        if new and jobs:
            for job in jobs:
                self.jobQueue[job.name] = job
            self.log("New jobs added. Enter command 'addjob' to add and enable jobs")

    def newFlags(self, jobName, flags={}, service=''):
        for team in flags.keys():
            self.scoreBot.flags.append([flags[team], team, jobName, service])


    # def createService(listServ):
    #     return [Service(l['name'], l['port'], l['type']) for l in listServ]
    def log(self, text):
        if self.DEBUG: print('[+] ' + text)

    def stop(self):
        self.log('Ctrl+C. Launcher Stopped by User')
        for job in self.jobs:
            self.log('Killing job: %s' % self.jobs[job].name)
            self.jobs[job].stop()
            del self.jobs[job]
        if not self.jobs:
            self.log('All jobs successfuly killed.')
        self.loader.kill()
        self.log('Logger stopped.')
        self.scorer.enabled = False
        self.log('Scorer stopped.')


    def parseCfg(self, fname):
        """
        This function initializes the launcher object based on a config file
        :param fname: type str: the name of the config file to use when initializing the launcher
                                file is formatted like:
                                    host=192.168.0.1
                                    debug=false

                                if options are a list, values should be comma deliminated ex:
                                    iprange=192.168.0.0,192.168.0.1
        :return:
        """
        with open(fname, 'r') as f:
            lines = [l.split('=') for l in f.readlines()]
            for line in lines:
                line = [line[0].replace('\n',''), line[1].replace('\n','')]
                if line[0] not in self.cfgOpts:
                    print(line[0] + ' is not a valid cfg opt...skipping')
                    continue

                if line[0] == self.cfgOpts[0]:
                    # initialize our team host ip address
                    self.log('Attempting to add IP Address %s as Host IP' % line[1])
                    self.cfg[line[0]] = IPAddress(line[1])

                elif line[0] == self.cfgOpts[1]:
                    # define the ip range to attack
                    # opt = line[1].split(',')
                    # self.log('Attempting to Init IP Range to: %s-%s' % (opt[0], opt[1]))
                    # self.cfg[line[0]] = IPRange(opt[0], opt[1])
                    with open(line[1],'r') as f:
                        for line in f.readlines():
                            self.hosts.append(line.strip())
                        self.log('Added IPs to self.hosts')

                elif line[0] == self.cfgOpts[2]:
                    # set debug mode
                    if line[1].lower() == 'false' or line[1].lower() == 'f':
                        self.DEBUG = False
                        self.log('Set Debug mode to False')
                    elif line[1].lower() == 'true' or line[1].lower() == 't':
                        self.DEBUG = True
                        self.log('Set Debug mode to True')

                elif line[0] == self.cfgOpts[3]:
                    # decide to send chaff or not
                    if line[1].lower() == 'false' or line[1].lower() == 'f':
                        self.randChaff = False
                        self.log('Set Random Chaff to False')
                    elif line[1].lower() == 'true' or line[1].lower() == 't':
                        self.randChaff = True
                        self.log('Set Random Chaff to True')

                elif line[0] == self.cfgOpts[4]:
                    # create an initial blacklist
                    ips = line[1].split(',')
                    self.blackList = self.blackList.extend(ips)
                    self.log('Added IPs: %s to Black List' % str(ips))

                elif line[0] == self.cfgOpts[5]:
                    # create an initial whitelist
                    ips = line[1].split(',')
                    self.whiteList = self.whiteList.extend(ips)
                    self.log('Added IPs: %s to White List' % str(ips))

                elif line[0] == self.cfgOpts[6]:
                    # init round tick time
                    self.cfg[line[0]] = int(line[1])
                    self.log('Set round tick length to %s' % line[1])

    @newThread
    def runJobs(self):
        while 1:
            for jobname in self.jobs:
                job = self.jobs[jobname]
                fail = False
                if job.enabled:
                    if time.time() - job.lastRun >= job.interval:
                        self.log('Attempting to run job: %s' % job.name)
                        try:
                            job.run()
                        except Exception as e:
                            print(str(e))
                            fail = True
                            self.log('Error running job: %s' % job.name)
                        if not fail:
                            self.log('Successfully started job: %s' % job.name)
            time.sleep(1)

    def start(self, crash=False):
        if crash: self.reboot()
        # prev = input('Would you like to import a previous job file? [y/n]: ').lower()
        # if prev in ['y','yes']:
        #     fi = input("Enter the file name: ")
        #     try:
        #         f = open(fi.strip(), "r")
        #         njobs = json.loads(f.read())
        #         f.close()
        #
        #         self.log("Attempting to import jobs file")
        #
        #         for key in njobs.keys():
        #             self.jobs[key] = Job(njobs[key]["name"], njobs[key]["location"], njobs[key])
        #
        #         print("\nSuccessfully imported jobs file")
        #     except:
        #         print("Could not import jobs file")
        self.runJobs()
        self.backup()
        self.enabled = True
        comp = Completer(self.commands.keys())
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(comp.complete)
        print(self.version)
        print("\nType 'help' to for usage\n")
        try:
            while self.enabled:
                res = input('> ')
                if res:
                    res = res.rstrip().split(' ')
                    if res[0] in self.commands:
                        self.log('Command entered: %s' % str(res))
                        if len(res) > 1:
                            self.commands[res[0]](*res[1:])
                        else:
                            self.commands[res[0]]()
                    else:
                        self.log("'%s': Not a valid command. Type 'help' for usage" % res[0])
        except KeyboardInterrupt:
            launcher.stop()
            print('Exiting.')
            sys.exit(0)

# Absolutely do not mess with the objects below this line
class Completer(object):
    """
    This is an autocompleter to be used with the python readline class
    sample implementation and documentation is located at:
    http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input
    """
    def __init__(self, commands):
        self.commands = commands
        self.re_space = re.compile('.*\s+$', re.M)

    def _listdir(self, root):
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _complete_path(self, path=None):
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p) for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def complete_extra(self, args):
        if not args:
            return self._complete_path('.')
        # treat the last arg as a path and complete it
        return self._complete_path(args[-1])

    def complete(self, text, state):
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()

        # show all commands
        if not line:
            return [c + ' ' for c in self.commands][state]
        # account for last argument ending in a space
        if self.re_space.match(buffer):
            line.append('')
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in self.commands:
            args = line[1:]
            if args:
                return (self.complete_extra(args) + [None])[state]
            return [cmd + ' '][state]
        results = [c + ' ' for c in self.commands if c.startswith(cmd)] + [None]
        return results[state]

class Service:
    def __init__(self, name, port, type):
        self.name = name
        self.port = port
        self.type = type

class Command:
    def __init__(self, name, desc, func, *usage):
        self.name = name
        self.desc = desc
        self.func = func
        self.usage = usage

    def __call__(self, *s):
        options = []
        for usage in range(len(self.usage)):
            if usage < len(s):
                (worked, res) = self.usage[usage](s[usage])
                if worked:
                    options.append(res)
                else:
                    if self.usage[usage].optional:
                        break
                    else:
                        print(res)
                        print(self)
                        return False
            else:
                if self.usage[usage].optional:
                    break
                else:
                    print(self)
                    return False

        self.func(*options)

    def __repr__(self, *args):
        return 'Usage: ' + self.name + ' ' + ' '.join(str(u) for u in self.usage)

class Usage:
    def __init__(self, func, usage, optional=False):
        self.func = func
        self.usage = usage
        self.optional = optional

    def __call__(self, args):
        return self.func(args) # ret tuple (bool success, ret val)

    def __repr__(self):
        return ''.join(['<' if not self.optional else '[', self.usage, '>' if not self.optional else ']'])


if __name__ == '__main__':
    while 1:
        crash = False
        launcher = Launcher()
        try:
            if crash:
                launcher.start(crash=True)
            else:
                launcher.start()
            crash = False
        except KeyboardInterrupt:
            launcher.stop()
            print('Exiting.')
            sys.exit(0)
        except Exception as e:
            launcher.log('FATAL ERROR: \n%s' % str(e))
            launcher.log('Restarting...')
            crash = True
            continue
