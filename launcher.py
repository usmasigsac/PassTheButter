import json
import time
import os
import sys
from netaddr import *
from threading import Thread
import readline
import re
import multiprocessing as mp

BACKUP_DIR = './backup'
BACKUP_JOBS = BACKUP_DIR + '/jobs'
BACKUP_SERVICES = BACKUP_DIR + '/services'
BACKUP_LAUNCHER = BACKUP_DIR + '/launcher'
BACKUP_CFG_FILE = BACKUP_LAUNCHER + '/cfg'
BACKUP_CONFIG = BACKUP_DIR + '/setup'


def newThread(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.setDaemon(True)
        thr.start()
    return wrapper

def newProc(f):
    def wrapper(*args, **kwargs):
        p = mp.Process(target=f, args=args, kwargs=kwargs)
        p.start()
    return wrapper

class Job:
    def __init__(self):
        self.name = ''
        self.path = ''
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

    def __repr__(self, *args):
        return 'Usage: ' + self.name + ' \n'.join(str(u) for u in self.usage)

class Usage:
    def __init__(self, func, usage, optional=False):
        self.func = func
        self.usage = usage
        self.optional = optional

    def __call__(self, *args):
        return self.func(s) # ret tuple (bool success, ret val)

    def __repr__(self):
        return ''.join(['<' if not self.optional else '[', self.usage, '>' if not self.optional else ']'])

class Launcher:
    def __init__(self, fname='config.cfg', debug=True):
        self.DEBUG = debug
        self.cfg = {}
        self.cfgOpts = ['host','iprange','debug','random_chaff','blacklist_targets','whitelist_targets']
        self.randChaff = False
        self.blackList = []
        self.whiteList = []
        self.parseCfg(fname)

        self.attackTypes = ['web','socket']
        self.jobs = {}
        self.hosts = []
        self.services = []
        self.commands = {
            "add": Command("add", "add a new job", self.createJob, Usage(self.checkFileExists, "job file"),
                           Usage(self.checkJobNotExists, "job name")),
            "enable": Command("enable", "begin running job", lambda job: job.enable(),
                              Usage(self.checkJobExists, "job name")),
            "disable": Command("disable", "stop running job and kill any threads it is currently running",
                               lambda job: job.disable(), Usage(self.checkJobExists, "job name")),
            "delete": Command("delete", "stop running job, kill any threads it is running, and remove it from launcher",
                              self.deleteJob, Usage(self.checkJobExists, "job name")),
            "list": Command("list", "list all information on current jobs", self.listJobs,
                            Usage(self.checkJobExists, "job name", True)),
            "stations": Command("stations", "change stations that a job will run on",
                                lambda job, stations: job.changeStations(stations),
                                Usage(self.checkJobExists, "job name"),
                                Usage(self.checkIfInts, "stations separated by commas")),
            "interval": Command("interval", "changes the time interval between running the job",
                                lambda job, interval=default_interval: job.changeInterval(interval),
                                Usage(self.checkJobExists, "job name"), Usage(
                    lambda i: (True, int(i)) if i.isdigit() and int(i) > 0 else (
                    False, "%s is not a valid interval (number greater than zero)" % i), "interval in seconds")),
            "help": Command("help", "show information from all commands", self.commandHelp,
                            Usage(self.commandExists, "command name", True)),
            "quit": Command("quit", "kill all jobs and exit out of launcher", self.quitLauncher),
            "print": Command("print", "print most recent lines from the log file",
                             lambda job, lines=10: job.printLog(lines), Usage(self.checkJobExists, "job name"), Usage(
                    lambda i: (True, int(i)) if i.isdigit() and int(i) > 0 else (
                    False, "%s is not a valid number of lines (number greater than zero)" % i), "number of lines",
                    True)),
            "export": Command("export", "export all jobs to a job file to be imported later", self.exportJobs,
                              Usage(lambda i: (True, str(i)), "export location"))
        }

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
        else: return (False, 'No File at location %' % location)

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
            print('Launcher %s' % self.version)
            print('All Commands:')
            for c in self.commands.keys():
                print('\t%s -> %s' % (self.commands[c].name, self.commands[c].help))
                print('\t\t' + self.commands[c])
        else:
            print('%s -> %s' % (cmd.name, cmd.help))
            print('\t' + str(cmd))

    def



    # def createService(listServ):
    #     return [Service(l['name'], l['port'], l['type']) for l in listServ]
    def log(self, text):
        if self.DEBUG: print('[+] ' + text)

    def stop(self):
        self.log('Ctrl+C. Launcher Stopped by User')
        for job in self.jobs:
            self.log('Killing job: %s' % job.name)
            job.delete()
        if not self.jobs:
            self.log('All jobs successfuly killed.')

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
                if line[0] not in self.cfgOpts:
                    print(line[0] + 'is not a valid cfg opt...skipping')
                    continue

                if line[0] == self.cfgOpts[0]:
                    # initialize our team host ip address
                    self.log('Attempting to add IP Address %s as Host IP' % line[1])
                    self.cfg[line[0]] = IPAddress(line[1])

                elif line[0] == self.cfgOpts[1]:
                    # define the ip range to attack
                    opt = line[1].split(',')
                    self.log('Attempting to Init IP Range to: %s-%s' % (opt[0], opt[1]))
                    self.cfg[line[0]] = IPRange(opt[0], opt[1])

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

    @newThread
    def runJobs(self):
        while 1:
            for job in self.jobs:
                fail = False
                if job.enabled:
                    if time.time() - job.lastRun >= job.interval:
                        self.log('Attempting to run job: %s' % job.name)
                        try:
                            job.beginJob()
                        except:
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

        comp = Completer(self.commands.keys())
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind('tab: complete')
        readline.set_completer(comp.complete)

        print("\nType 'help' to for usage\n")
        while 1:
            res = input('> ')
            if res:
                res = res.rstrip().split(' ')
                if res[0] in self.commands:
                    self.log('Command entered: %s' % str(res))
                    self.commands[res[0]](*res[1:])
                else:
                    self.log("'%s': Not a valid command. Type 'help' for usage" % res[0])




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


if __name__ == '__main__':
    while 1:
        crash = False
        try:
            if crash:
                Launcher.start(crash=True)
            else:
                Launcher.start()
            crash = False
        except KeyboardInterrupt:
            Launcher.stop()
            print('Exiting.')
            sys.exit(0)
        except:
            crash = True
            continue