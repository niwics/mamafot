#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Skript pro nastaveni spravneho opravneni slozkam s fotkami.
(c) Miroslav Kvasnica, niwi.cz, june 2013
'''

import os
import re
import ConfigParser

class ConfigException(Exception):
    pass
#endclass
    
class Worker:

    ACCESS_ALLOW = 0750
    ACCESS_DENY = 0700
    RE_DAY = re.compile('^[12]\d\d\d-[0123]?\d-[0123]?\d$')
    DIRTYPE_OTHER = 0
    DIRTYPE_ROOT = 1
    DIRTYPE_YEAR = 2
    DIRTYPE_MONTH = 3
    DIRTYPE_DAY = 4
    
    def __init__(self, filename):
        '''
        Open config file
        '''
        self.filename = os.path.abspath(filename)
        self.includeDays = []
        self.includePaths = []
        self.excludePaths = []
        try:
            self.readConfig()
        except ConfigException, e:
            print "Error while parsing config file: %s" % e
            exit(1)
    #enddef
    
    
    def readConfig(self):
        '''
        Read all folders from the config file
        '''
        print 'Starting to parsing config file "%s"' % self.filename
        config = ConfigParser.RawConfigParser()
        config.read(self.filename)
        self.baseDir = config.get('Control', 'BaseDir')
        
        # list of included days
        try:
            days = config.get('Control', 'IncludeDays').split()
        except:
            days = []
        for day in days:
            if day.strip() == '' or day.startswith('#'):
                continue
            if not Worker.RE_DAY.match(day):
                raise ConfigException("Wrong day string format: %s" % day)
            self.includeDays.append(day)
        
        # list of included paths
        try:
            paths = config.get('Control', 'IncludePaths').split()
        except:
            paths = []
        for path in paths:
            if path.strip() != '' and not path.startswith('#'):
                self.includePaths.append(path)
        
        # list of excluded paths
        try:
            paths = config.get('Control', 'ExcludePaths').split()
        except:
            paths = []
        for path in paths:
            if path.strip() != '' and not path.startswith('#'):
                if path.startswith('/'):
                    raise ConfigException("Absolute paths are not allowed: %s" % path)
                self.excludePaths.append(path)
    #enddef
    
        
    def setPermissions(self):
        '''
        Set permissions for all files and folders in baseDir
        '''
        self.processDir(self.baseDir, Worker.DIRTYPE_ROOT)
    #enddef
    
        
    def processDir(self, currentDir, dirtype):
        '''
        Set permissions for the directory and its content
        '''
        rootString = 'root' if dirtype == Worker.DIRTYPE_ROOT else ''
        print 'Processing the %s directory "%s"...' % (rootString, currentDir)
        
        # allow access to this dir
        os.chmod(currentDir, Worker.ACCESS_ALLOW)
    
        # iterate over the all content in current dir
        for root, dirs, files in os.walk(currentDir):
            for file in files:
                access = ACCESS_ALLOW if file in self.includePaths else ACCESS_DENY
                os.chmod(os.path.join(currentDir, file), access)
            for dir in dirs:
                if dirtype == self.DIRTYPE_ROOT:
                    specialCondition = Worker.RE_YEAR.match(dir)
                    subdirtype = self.DIRTYPE_YEAR
                else:
                    subdirtype = self.DIRTYPE_OTHER
                if dir in self.includePaths or specialCondition:
                    subdir = os.path.join(currentDir, dir)
                    self.processDir(subdir, subdirtype)
                else:
                    os.chmod(os.path.join(self.baseDir, dir), ACCESS_DENY)
#endclass
        

if __name__ == "__main__":
    w = Worker("mamafot.rules")
    w.setPermissions()
    
