#!/usr/bin/python

import argparse
import pprint
import gc
import subprocess
import re
from collections import defaultdict
###### Global variables

Path = "/Users/guang.yang/windsor/icinga2/conf.d"


def main(args):
    ###get all roles in an array, contains roles and related servers belong to the role
    roles=getrole(Path)
    
    ###get all profiles in an array contains profiles and roles are using the profile
    profiles=getprofile(Path,roles)
    
    ###get all services in an array contains services and profiles are using the service
    services=getservices(Path)

    ###create an empty dictionary for the roles, profiles and services
    RPS = {}
    
    ### initiate all the roles objects
    for item in roles:
        ###grep the name of the object from the roles dictionary, and then initate an role object, put it into the Array--RPS
        RPS[item]=Role(item)
   
#        ###call the subroutine for Role object, to add the servers to the related role
#        for ss in roles[item]:
#            RPS[item].add_servers(ss)
#
    ### put the related profiles to the role
    for item in profiles:
        ###instantiate the profile class
        Profile(item)
        for rs in profiles[item]:
            tmp=Profile(item)
            RPS[rs].add_profile(tmp.name,tmp)
    

    ### put the related services to the profile, we will 
#    for item in services:
#        ###instantiate the Service class
#        print 
#        print item
#        for i2 in services[item]:
#            print i2
#        


#    for item in RPS:
#        print item
#        #RPS[item].list_profile()
#        for p in RPS[item].profiles:
#            print p
#        RPS[item].list_server()
#        for i in Role(item).profiles:
#            Profile(i).list_service

def getrole(location):
    ###create the list command, it will pickup all the roles in the host define files.
    getrolecmd = "grep vars.roles %s/hosts.d/* -r" % (location)
    
    ###return an array which contains all the roles. Since the default structure for this variable is dictionary contains array, so we have to force it to use array.
    allroles=defaultdict(list)

    output= subprocess.Popen(getrolecmd,shell=True,stdout=subprocess.PIPE)
    data = output.stdout.read().splitlines()

    reg=".*/(.*).conf.*\"(.*)\""
    for line in data:
        ###use re to get host and role set and role as key, servers as value
        ma=re.search(reg,line)
        #allroles[re.search(reg,line).group(2)].append(re.search(reg,line).group(1))
        if allroles[re.search(reg,line).group(2)]:
            allroles[re.search(reg,line).group(2)].add_servers(re.search(reg,line).group(1))
        else:
            allroles[re.search(reg,line).group(2)]=Role(re.search(reg,line).group(2))
            allroles[re.search(reg,line).group(2)].add_servers(re.search(reg,line).group(1))
    
    return allroles

def getprofile(location,roles):
    ###create the list command, it will pickup all the roles in the host define files.
    getrolecmd = "grep \"assign where\" %s/profile/* -r" % (location)
    
    ###return an array which contains all the profiles, and the roles those are using the profiles. Since the default structure for this variable is dictionary contains array, so we have to force it to use array.
    allprofiles=defaultdict(list)

    output= subprocess.Popen(getrolecmd,shell=True,stdout=subprocess.PIPE)
    data = output.stdout.read().splitlines()
    reg =".*\/(.*).conf.*assign where\s(\"(.*)\")?"    
    for line in data:
        ###use re to get host and role set, profile as key role as value.
        ###when the profile is not profiles-common,instantiate the profile object, and add the profile to Role objects 
        if re.search(reg,line).group(2):
            ###if the profile has already been initialized, just add the profile to the related role, re.search(reg,line).group(1) is the profile, re.search(reg,line).group(2) is the role name
            if allprofiles[re.search(reg,line).group(1)]:
                roles[re.search(reg,line).group(2)].add_profile(re.search(reg,line).group(1))
            ###if the profile is not created yet, instantiate the profile, and then added to the role instance, same as the previous step
            else:
                allprofiles[re.search(reg,line).group(1)]=Profile(re.search(reg,line).group(1))
                roles[re.search(reg,line).group(2)].add_profile(re.search(reg,line).group(1))
        else :
                allprofiles[re.search(reg,line).group(1)]=Profile(re.search(reg,line).group(1))
                for item in roles:
                    roles[item].add_profile(re.search(reg,line).group(1))

    print allprofiles
    return allprofiles

def getservices(location):
    ###create the list command, it will pickup all the roles in the host define files.
    getrolecmd = "grep \"assign where\" %s/services.d/profile-*/* -r" % (location)
    
    ###return an array which contains all the services, and the profiles those are using the services. Since the default structure for this variable is dictionary contains array, so we have to force it to use array.
    allservices=defaultdict(list)

    output= subprocess.Popen(getrolecmd,shell=True,stdout=subprocess.PIPE)
    data = output.stdout.read().splitlines()
    reg =".*\/(.*)-profile.*conf.*assign where.*\"(.*)\""
    for line in data:
        if re.search(reg,line).group(2):
            ###use re to get host and role set
            allservices[re.search(reg,line).group(1)].append(re.search(reg,line).group(2))
            #print "profile is %s, services is %s" % (re.search(reg,line).group(2),re.search(reg,line).group(1))
    return allservices

class Role(object):  
    ###define tow arrays, one for all the servers belongs to the role, the other one is for all the profiles belongs to the role
    #init will name the role
    def __init__(self,name):
        self.name=name
        self.servers=[]
        self.profiles=[]
    
    def add_profile(self,profilename):
        if profilename not in self.profiles:
            self.profiles.append(profilename)

    def list_profile(self):
            print self.profiles

    def list_server(self):
            print self.servers

    def add_servers(self,servernames):
        if servernames not in  self.servers:
            self.servers.append(servernames) 

class Profile(object):  
    def __init__(self,name):
        self.name=name
        self.services=[]
    
    def add_service(self,servicename):
        if servicename not in  self.services:
            self.services.append(servicename)

    def list_service(self):
        print self.aservices

class Service(object):
    def __init__(self,name):
        self.name=name
        self.checks=[]

    def addto_profile(self):
        if profilename not in self.profiles:
            self.profiles.append(profilename)

def readfile(file):
	'''
	method to read a file and return its content
	'''
	content = open(file).read().splitlines()
	return content



if __name__ == '__main__':
	parser = argparse.ArgumentParser(
	description='It will list all the roles we have now, \
		and all the related profiles for each role.')
	parser.add_argument(
	'-L', '--letter', type=str, help='function of input param', required=False)
	parser.add_argument(
	'-W', '--whatever', type=int, help='another input param', required=False)
	args = parser.parse_args()
	main(args)
