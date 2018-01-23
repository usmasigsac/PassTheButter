#! /usr/bin/env python3

import importlib

class Job:
    def __init__(self, name, loader):
        self.path = name
        self.name = name.split('/')[-1]
        self.payload = importlib.import_module