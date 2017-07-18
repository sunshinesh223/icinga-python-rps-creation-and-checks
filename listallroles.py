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
    profiles=getprofile(Path)
    
    ###get all services in an array contains services and profiles are using the service
    services=getservices(Path)

    for item in services:
        print services[item].name
        #print services[item].profiles
        for i in services[item].profiles:
            print i
            print profiles[i].name

#    for item in roles:
#        print roles[item].name
#        roles[item].list_server()
#        roles[item].list_profile()
#
#    for item in profiles:
#        print profiles[item].name
#        profiles[item].list_service()
#        print profiles[item].roles
def getrole(location):
    ###create the list command, it will pickup all the roles in the host define files.
    getrolecmd = "grep vars.roles %s/hosts.d/* -r" % (location)
    
    ###return an array which contains all the roles. Since the default structure for this variable is dictionary contains array, so we have to force it to use array.
    allroles=defaultdict(dict)

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

def getprofile(location):
    ###create the list command, it will pickup all the roles in the host define files.
    getrolecmd = "grep \"assign where\" %s/profile/* -r" % (location)
    
    ###return an array which contains all the profiles, and the roles those are using the profiles. Since the default structure for this variable is dictionary contains array, so we have to force it to use array.
    allprofiles=defaultdict(dict)

    output= subprocess.Popen(getrolecmd,shell=True,stdout=subprocess.PIPE)
    data = output.stdout.read().splitlines()
    reg =".*\/(.*).conf.*assign where\s(\"(.*)\")?"    
    for line in data:
        ###use re to get host and role set, profile as key role as value.
        ###when the profile is not profiles-common,instantiate the profile object, and add the profile to Role objects 
        if re.search(reg,line).group(2):
            ###if the profile has already been initialized, just add the profile to the related role, re.search(reg,line).group(1) is the profile, re.search(reg,line).group(2) is the role name
            if allprofiles[re.search(reg,line).group(1)]:
               allprofiles[re.search(reg,line).group(1)].add_role(re.search(reg,line).group(3))
            ###if the profile is not created yet, instantiate the profile, and then added to the role instance, same as the previous step
            else:
               allprofiles[re.search(reg,line).group(1)]=Profile(re.search(reg,line).group(1))
               allprofiles[re.search(reg,line).group(1)].add_role(re.search(reg,line).group(3))
        else :
                allprofiles[re.search(reg,line).group(1)]=Profile(re.search(reg,line).group(1))
                allprofiles[re.search(reg,line).group(1)].add_role("applytoallroles")

    return allprofiles

def getservices(location):
    ###create the list command, it will pickup all the roles in the host define files.
    getrolecmd = "grep \"assign where\" %s/services.d/profile-*/* -r" % (location)
    
    ###return an array which contains all the services, and the profiles those are using the services. Since the default structure for this variable is dictionary contains array, so we have to force it to use array.
    allservices=defaultdict(dict)

    output= subprocess.Popen(getrolecmd,shell=True,stdout=subprocess.PIPE)
    data = output.stdout.read().splitlines()
    reg =".*\/(.*)-profile.*conf.*assign where.*\"(.*)\""
    for line in data:
        ### if the instance of service has been instantiated, then just add the profile to its list
        if allservices[re.search(reg,line).group(1)]:
            allservices[re.search(reg,line).group(1)].add_profile(re.search(reg,line).group(2))
        ### otherwise, create the instance and then add the profile to it
        else:
            allservices[re.search(reg,line).group(1)]=Service(re.search(reg,line).group(1))
            allservices[re.search(reg,line).group(1)].add_profile(re.search(reg,line).group(2))
    
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
        self.roles=[]
    
    def add_service(self,servicename):
        if servicename not in  self.services:
            self.services.append(servicename)

    def add_role(self,rolename):
        if rolename not in  self.roles:
            self.roles.append(rolename)

    def list_service(self):
        print self.services

    def list_role(self):
        print self.roles

class Service(object):
    def __init__(self,name):
        self.name=name
        self.checks=[]
        self.profiles=[]

    def add_profile(self,profilename):
        if profilename not in self.profiles:
            self.profiles.append(profilename)

    def list_profile(self):
        print self.profiles

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
