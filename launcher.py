import time
import os
from netaddr import *
from threading import Thread

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
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
        self.jobs = []
        self.services = []


    # def createService(listServ):
    #     return [Service(l['name'], l['port'], l['type']) for l in listServ]
    def log(self, text):
        if self.DEBUG: print(text)

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


    def run(self):
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



if __name__ == '__main__':
    while 1:
        try:
            Launcher.start()
        except:
            continue