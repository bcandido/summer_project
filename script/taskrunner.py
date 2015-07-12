#!/usr/bin/python

import xml.etree.ElementTree as ElementTree
from xml.dom import minidom
import subprocess
from threading import Thread
import string
import sys
import re

# DEFINES
ARG_DESCRIPTOR = "-D"
ARG_PLUGIN = "-P"
ARG_PARALLEL = "--parallel"

def main():

	if ARG_DESCRIPTOR in sys.argv:
		descriptor = getDescriptor(sys.argv)
	
	if ARG_PLUGIN in sys.argv:
		pluginName = getPlugin(sys.argv)
		print pluginName
		plugin = descriptor.findall('./plugin[@name="'+pluginName+'"]')
		runPlugin(plugin[0])

#---------------------------------------------------------------------------------
def getDescriptor(arguments):
	idx = arguments.index("-D")
	fileDescriptor = arguments[idx+1]
	return ElementTree.parse(fileDescriptor)

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
			subCmd = []
			for i in range(0, len(cmd.count("|"))):
				if cmd[i] != "|":
					
			if cmd.count("|") > 0:
				for c in cmd:
					
			else:
				output = subprocess.check_output(cmd, shell=False)
			
			#print output
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