#!/usr/bin/env python

import axis
import time

import os
import sys
import getopt
import asynchat
import asyncore
import socket

DEFAULT_PORT = 31337

class Controller:
	'''
	Class representing a motor controller

	'''
	def __init__(self):
		self.numAxes = 3
		self.axisNameList = ['X','Y','Z']
		self.axisNumberList = [str(x) for x in range(1, self.numAxes+1)]

		self.commandDict = {3:{'MV':self.moveAxis, 
		                       'ACC':self.setAcceleration, 
				       'VEL':self.setVelocity,
				       'LL':self.setLowLimit,
				       'HL':self.setHighLimit},
		                    2:{'POS?':self.queryPosition, 
				       'ST?':self.queryStatus,
				       'ACC?':self.queryAcceleration,
				       'VEL?':self.queryVelocity,
				       'LL?':self.queryLowLimit,
				       'HL?':self.queryHighLimit,
				       'AB':self.stopAxis}} 
		self.axisDict = {}
		self.axisList = []
		self.enforceLimits = False

		for i in range(self.numAxes):
			self.axisList.append( axis.Axis() )
			self.axisDict[self.axisNameList[i]] = i
			self.axisDict[self.axisNumberList[i]] = i

		#!print self.axisDict
		#!print self.axisDict.keys()

	def handleCommand(self, command):
		# Check for empty command string
		if command == '':
			retVal = None
		else:
			args = command.split(' ')
			numArgs = len(args)
			#!print args
			#!print self.axisDict.keys()
			# Check for incorrect number of args
			if numArgs not in self.commandDict.keys():
				retVal = "Argument error"
			# Check for incorrect axis names
			elif args[0] not in self.axisDict.keys():
				retVal = "Axis name error"
			else:
				# Check for invalid commands
				if args[1] not in self.commandDict[numArgs].keys():
					retVal = "Command error"
				else:
					if numArgs == 2:
						retVal = self.commandDict[numArgs][args[1]](args[0])
					elif numArgs == 3:
						retVal = self.commandDict[numArgs][args[1]](args[0], args[2])
					else:
						retVal = "Strange error"

		return retVal

	def queryPosition(self, axis):
		return self.axisList[self.axisDict[axis]].readPosition()

	def queryStatus(self, axis):
		return self.axisList[self.axisDict[axis]].readStatus()

	def moveAxis(self, axis, pos):
		return self.axisList[self.axisDict[axis]].move(float(pos))

	def stopAxis(self, axis):
		return self.axisList[self.axisDict[axis]].stop()

	def setVelocity(self, axis, velocity):
		return self.axisList[self.axisDict[axis]].setVelocity(float(velocity))

	def queryVelocity(self, axis):
		return self.axisList[self.axisDict[axis]].readVelocity()

	def setAcceleration(self, axis, acceleration):
		return self.axisList[self.axisDict[axis]].setAcceleration(float(acceleration))

	def queryAcceleration(self, axis):
		return self.axisList[self.axisDict[axis]].readAcceleration()

	def queryHighLimit(self, axis):
		return self.axisList[self.axisDict[axis]].readHighLimit()

	def setHighLimit(self, axis, highLimit):
		return self.axisList[self.axisDict[axis]].setHighLimit(float(highLimit))

	def queryLowLimit(self, axis):
		return self.axisList[self.axisDict[axis]].readLowLimit()

	def setLowLimit(self, axis, lowLimit):
		return  self.axisList[self.axisDict[axis]].setLowLimit(float(lowLimit))

class ConnectionDispatcher(asyncore.dispatcher):
	def __init__(self, port):
		asyncore.dispatcher.__init__(self)
		self.port = port
		self.device = Controller()
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind(("", port))
		self.listen(5)

	def handle_accept(self):
		ConnectionHandler(self.accept(), self.device)


class ConnectionHandler(asynchat.async_chat):
	## regular expressions, if necessary, can go here

	def __init__(self, (conn, addr), device):
		asynchat.async_chat.__init__(self, conn)
		self.set_terminator("\r")
		#
		self.outputTerminator = "\r\n"
		self.device = device
		self.buffer = ""

	def collect_incoming_data(self, data):
		self.buffer = self.buffer + data

	def found_terminator(self):
		data = self.buffer
		self.buffer = ""
		self.handleClientRequest(data)

	def handleClientRequest(self, request):
		request = request.strip()
		## handle actual commands here
		print request

		# Commands of form
		# X MV 400
		response = self.device.handleCommand(request)

		if response != None:
			self.sendClientResponse("%s" % response)

		return

	def sendClientResponse(self, response=""):
		data = response + self.outputTerminator
		self.push(data)


def getProgramName(args=None):
	if args == None:
		args = sys.argv
	if len(args) == 0 or args[0] == "-c":
		return "PROGRAM_NAME"
	return os.path.basename(args[0])


def printUsage():
	print """\
Usage: %s [-ph]

Options:
  -p,--port=NUMBER   Listen on the specified port NUMBER for incoming
                     connections (default: %d)
  -h,--help          Print usage message and exit\
""" % (getProgramName(), DEFAULT_PORT)


def parseCommandLineArgs(args):
	(options, extra) = getopt.getopt(args[1:], "p:h", ["port=", "help"])

	port = DEFAULT_PORT

	for eachOptName, eachOptValue in options:
		if eachOptName in ("-p", "--port"):
			port = int(eachOptValue)
		elif eachOptName in ("-h", "--help"):
			printUsage()
			sys.exit(0)

	if len(extra) > 0:
		print "Error: unexpected command-line argument \"%s\"" % extra[0]
		printUsage()
		sys.exit(1)

	return port


def main(args):
	port = parseCommandLineArgs(args)
	server = ConnectionDispatcher(port)
	try:
		asyncore.loop()
	except KeyboardInterrupt:
		print
		print "Shutting down server..."
		sys.exit(0)


if __name__ == '__main__':
	try:
		main(sys.argv)
	except Exception, e:
		if isinstance(e, SystemExit):
			raise e
		else:
			print "Error: %s" % e
			sys.exit(1)
