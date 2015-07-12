#!/usr/bin/python

import xml.etree.ElementTree as ElementTree
from threading import Thread
from xml.dom import minidom
#from lxml import etree, objectify
import subprocess
#import StringIO
import string
import sys
import re

# DEFINES
ARG_DESCRIPTOR = "-D"
ARG_PLUGIN = "-P"
ARG_PARALLEL = "--parallel"

DTD_FILE = "descriptor.dtd"

def main():

	if ARG_DESCRIPTOR in sys.argv:
		descriptor = getDescriptor(sys.argv)
	
	if ARG_PLUGIN in sys.argv:
		pluginName = getPlugin(sys.argv)
		plugin = descriptor.findall('./plugin[@name="'+pluginName+'"]')
		runPlugin(plugin[0])

#---------------------------------------------------------------------------------
def getDescriptor(arguments):
	idx = arguments.index("-D")
	fileDescriptor = arguments[idx+1]
	
	if validDescriptor(fileDescriptor):
		ret = ElementTree.parse(fileDescriptor)
	else:
		ret = None
		
	return ret

#---------------------------------------------------------------------------------
def validDescriptor(xml_file):
	from lxml import etree, objectify
	from StringIO import StringIO

	f = open(xml_file)
	xml_doc = f.read()
	f.close()
	
	f = open(DTD_FILE)
	dtd_doc = f.read()
	f.close()

	dtd = etree.DTD(StringIO(dtd_doc))
	tree = objectify.parse((xml_doc))
	#return dtd.validate(tree)
	return True

#---------------------------------------------------------------------------------
def getPlugin(arguments):
	idx = arguments.index("-P")
	return arguments[idx+1]
	

#---------------------------------------------------------------------------------
def runPlugin(plugin=None):
	taskList = plugin.findall("./taskList/task")
	
	threading = False
	if ARG_PARALLEL in sys.argv:
		threading = True
	runTasks(taskList, threading)

#---------------------------------------------------------------------------------
def runTasks(taskList, threading=False):
	if threading:
		threads = []
		for task in taskList:
			task = task.findall("./command")
			commands = []
			commands.append(task[0].text)
			t = Thread(target=execute, args=(commands,))
			threads.append(t)
			t.start()
			
	elif not(threading):
		commands = []
		for task in taskList:
			task = task.findall("./command")
			commands.append(task[0].text)
		execute(commands)

#---------------------------------------------------------------------------------
def execute(commands=None):
	if commands != None:
		for cmd in commands:
			cmd = cmd.split(' ')
			while '' in cmd:
				cmd.remove('')
			cmd = updateCommand(cmd)
			#subCmd = []
			#for i in range(0, len(cmd.count("|"))):
				#if cmd[i] != "|":
					
			#if cmd.count("|") > 0:
				## implement logic
			#else:
				#output = subprocess.check_output(cmd, shell=False)
			
			output = subprocess.check_output(cmd, shell=False)
			print output
	return

#---------------------------------------------------------------------------------
def updateCommand(command):
	for cmd in command:
		if cmd[0] == "%":
			arg = cmd.replace("%", "-")
			if (arg.upper() in sys.argv) or (arg.lower() in sys.argv):
				command = replaceArg(command, cmd, arg)
	return command

#---------------------------------------------------------------------------------
def replaceArg(command, cmd, arg):
	indexArg = command.index(cmd)
	indexValue = sys.argv.index(arg) + 1
	command[indexArg] = sys.argv[indexValue]
	
	return command

#---------------------------------------------------------------------------------
main()