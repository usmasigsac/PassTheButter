#! /usr/bin/env python3

class Job:
    def __init__(self, name, loader):
        self.path = name
        self.name = name.split('/')[-1]
        self.payload = ''