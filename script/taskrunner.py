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
ARG_TASKVIEW = "--list"

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
	return ElementTree.parse(fileDescriptor)

#---------------------------------------------------------------------------------
def getPlugin(arguments):
	idx = arguments.index("-P")
	return arguments[idx+1]
	

#---------------------------------------------------------------------------------
def runPlugin(plugin=None):
	taskList = plugin.findall("./taskList/task")
	
	if ARG_TASKVIEW in sys.argv:
		taskDescription = getTaskDescription(taskList)
		showTaskDescription(taskDescription)
	else:
		threading = False
		if ARG_PARALLEL in sys.argv:
			threading = True
		runTasks(taskList, threading)

#---------------------------------------------------------------------------------
def getTaskDescription(taskList):
	taskDescription = {}
	task_idx = 0
	for task in taskList:
		description = task.findall("./description")
		taskDescription[task_idx] = description[0].text.strip()
		task_idx = task_idx + 1
	return taskDescription

#---------------------------------------------------------------------------------
def showTaskDescription(taskDescription):
	for key in taskDescription.keys():
		print "Task %s: %s"%(key, taskDescription[key])

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