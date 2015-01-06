#!/usr/bin/env python

import axis
import time

import asynchat
import asyncore
import socket

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
				       'HL?':self.queryHighLimit}} 
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
		# X MV 5.0
		response = self.device.handleCommand(request)

		if response != None:
			self.sendClientResponse("%s" % response)

		return

	def sendClientResponse(self, response=""):
		data = response + self.outputTerminator
		self.push(data)

if __name__ == '__main__':
	#!myc = Controller()
	#!pos = myc.axisList[0].readPosition()
	#!st = myc.axisList[0].readStatus()
	#!print st, pos
	#!myc.axisList[0].move(5.0)
	#!for i in range(65):
	#!	pos = myc.axisList[0].readPosition()
	#!	st = myc.axisList[0].readStatus()
	#!	print st, pos
	#!	time.sleep(0.1)
	port = 31337

	server = ConnectionDispatcher(port)
	asyncore.loop()
