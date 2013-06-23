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

    ACCESS_ALLOW = '0750'
    ACCESS_DENY = '0700'
    RE_DAY = re.compile('^[12]\d\d\d-[0123]?\d-[0123]?\d$')
    DIRTYPE_OTHER = 0
    DIRTYPE_YEAR = 1
    DIRTYPE_MONTH = 2
    DIRTYPE_DAY = 3
    
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
        days = config.get('Control', 'IncludeDays').split()
        for day in days:
            if day.strip() == '' or day.startswith('#'):
                continue
            if not Worker.RE_DAY.match(day):
                raise ConfigException("Wrong day string format: %s" % day)
            self.includeDays.append(day)
        
        # list of included paths
        paths = config.get('Control', 'IncludePaths').split()
        for path in paths:
            if path.strip() != '' and not path.startswith('#'):
                self.includePaths.append(path)
        
        # list of excluded paths
        paths = config.get('Control', 'ExcludePaths').split()
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
        # allow access to the baseDir
        os.chmod(self.baseDir, ALLOW_ACCESS)
        
        # iterate over the all content in baseDir
        for root, dirs, files in os.walk(self.baseDir):
            print 'Processing the root directory "%s"...' % self.baseDir
            for file in files:
                access = ACCESS_ALLOW if file in self.includePaths else ACCESS_DENY
                os.chmod(os.path.join(self.baseDir, file), access)
            for dir in dirs:
                if dir in self.includePaths or Worker.RE_YEAR.match(dir):
                    subdir = os.path.join(self.baseDir, dir)
                    dirtype = self.DIRTYPE_YEAR if Worker.RE_YEAR.match(dir) else self.DIRTYPE_OTHER
                    self.processDir(subdir, dirtype)
                else:
                    os.chmod(os.path.join(self.baseDir, dir), ACCESS_DENY)
    #enddef
    
        
    def processDir(self, currentDir, dirtype):
        '''
        Set permissions for the directory and its content
        '''
        # allow access to this dir
        os.chmod(currentDir, ALLOW_ACCESS)
    
        # iterate over the all content in current dir
        for root, dirs, files in os.walk(currentDir):
            print 'Processing the directory "%s"...' % currentDir
            for file in files:
                access = ACCESS_ALLOW if file in self.includePaths else ACCESS_DENY
                os.chmod(os.path.join(currentDir, file), access)
            for dir in dirs:
                if dir in self.includePaths or Worker.RE_YEAR.match(dir):
                    subdir = os.path.join(currentDir, dir)
                    dirtype = self.DIRTYPE_YEAR if Worker.RE_YEAR.match(dir) else self.DIRTYPE_OTHER
                    self.processDir(subdir, dirtype)
                else:
                    os.chmod(os.path.join(self.baseDir, dir), ACCESS_DENY)
#endclass
        

if __name__ == "__main__":
    w = Worker("mamafot.rules")
    w.setPermissions()
    
