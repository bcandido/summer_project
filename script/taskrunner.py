#!/usr/bin/python

import xml.etree.ElementTree as ElementTree
from xml.sax.saxutils import unescape
from xml.dom.minidom import Document
import subprocess
from threading import Thread
import string
import time
import sys
import re

import StringIO
import lxml.etree as etree
from xml.etree.ElementTree import Element, SubElement, Comment

# ARGUMENT DEFINES
ARG_DESCRIPTOR = "-D"
ARG_PLUGIN = "-P"
ARG_PARALLEL = "--parallel"
ARG_TASKVIEW = "--list"
ARG_OUTPUT =  "--xml"

def main():

	if ARG_DESCRIPTOR in sys.argv:
		descriptor = getDescriptor(sys.argv)
	
	if ARG_PLUGIN in sys.argv:
		pluginName = getPlugin(sys.argv)
		plugin = descriptor.findall('./plugin[@name="'+pluginName+'"]')
		
		start_time = time.clock()
		runPlugin(plugin[0])
		executionTime = time.clock() - start_time
		
		if executionTime != None:
			print "All tasks were executed in %s seconds"%(executionTime)

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
		if description:
			taskDescription[task_idx] = description[0].text.strip()
		else:
			taskDescription[task_idx] = "No Task Description"
		task_idx = task_idx + 1
	return taskDescription

#---------------------------------------------------------------------------------
def showTaskDescription(taskDescription):
	for key in taskDescription.keys():
		print "Task %s: %s"%(key, taskDescription[key])

#---------------------------------------------------------------------------------
def getCommandList(task=None):
	if task == None:
		return
	
	commands = task.findall("./command")
	commandList = []
	for cmd in commands:
		commandList.append(cmd.text)
	return commandList

#---------------------------------------------------------------------------------
def getTaskList(taskList=None):
	if taskList == None:
		return
	
	tasks = taskList.findall("./task")
	taskList = []
	for task in taskList:
		taskList.append(task.text)
	return taskList

#---------------------------------------------------------------------------------
def runTasks(taskList, threading=False):
	if ("--xml" not in sys.argv) and ("--parallel" in sys.argv):
		print "Is NOT recommended run --parallel option in display mode"
		print "It may cause misunderstand for the user"
	
	outputList = []
	if threading:
		threads = []
		for task in taskList:
			commandList = getCommandList(task)
			t = Thread(target=execute, args=(commandList,))
			threads.append(t)
			t.start()
	
	elif not(threading):
		for task in taskList:
			commandList = getCommandList(task)
			execute(commandList, outputList)
	
	handleOutput(outputList)

#---------------------------------------------------------------------------------
def execute(commands=None, outputList=[]):
	if commands != None:
		for cmd in commands:
			cmd = cmd.strip().split(' ')
			#while '' in cmd:
				#cmd.remove('')
			cmd = updateCommand(cmd)
			output = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE).communicate()
			outputList.append((commands, output[0]))

#---------------------------------------------------------------------------------
def updateCommand(command):
	for cmd in command:
		if cmd[0] == "$":
			arg = cmd.replace("$", "-")
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
def handleOutput(outputList):
	
	if "--xml" in sys.argv:
		saveXML(outputList)
	else:
		print outputList

#---------------------------------------------------------------------------------
def saveXML(outputList):
	
	doc = Document()
	taskList = doc.createElement('taskList')
	doc.appendChild(taskList)
	
	for elem in outputList:
		commandList, output = elem
		task = doc.createElement('task')
		for command in commandList:
			command = " ".join(updateCommand(command.strip().split(' ')))
			cmd = doc.createElement('command')
			cmd.appendChild(doc.createTextNode(command))
			task.appendChild(cmd)
			
		output = output.strip().split('\n')
		out = doc.createElement('output')
		for line in output:
			out.appendChild(doc.createTextNode(line))
		
		task.appendChild(out)
		taskList.appendChild(task)
	
	f = open('output_task.xml', 'w')
	f.write(unescape(doc.toprettyxml()))
	f.close()
	
	#print doc.toprettyxml()

#---------------------------------------------------------------------------------
def getSubCommandList(command):
	subcmd = []
	list = []
	for c in command:
		if c != "|":
			list.append(c)
		else:
			subcmd.append(list)
			list = []
		
	subcmd.append(list)
	return subcmd

#---------------------------------------------------------------------------------
main()