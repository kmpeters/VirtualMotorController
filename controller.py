#!/usr/bin/env python

import axis
import time

class Controller:
	'''
	Class representing a motor controller

	'''
	def __init__(self):
		self.numAxes = 3
		self.axisNameList = ['X','Y','Z']
		self.axisNumberList = [str(x) for x in range(1, self.numAxes+1)]

		self.commandDict = {3:{'MV':self.moveAxis,
		                       'POS':self.setPosition,
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

	def strToNum(self, inputString):
		# Return an int since the controller has units of counts
		return int(round(float(inputString)))

	def refinePos(self, inputPos):
		# Convert a raw position from the axis class to something suitable for output
		# Return an int since the controller has units of counts
		return int(round(inputPos))

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
						retVal = self.commandDict[numArgs][args[1]](args[0], self.strToNum(args[2]))
					else:
						retVal = "Strange error"

		return retVal

	def queryPosition(self, axis):
		# round the result, since the controller units are counts
		return self.refinePos(self.axisList[self.axisDict[axis]].readPosition())

	def setPosition(self, axis, pos):
		return self.axisList[self.axisDict[axis]].setPosition(pos)

	def queryStatus(self, axis):
		return self.axisList[self.axisDict[axis]].readStatus()

	def moveAxis(self, axis, pos):
		return self.axisList[self.axisDict[axis]].move(pos)

	def stopAxis(self, axis):
		return self.axisList[self.axisDict[axis]].stop()

	def setVelocity(self, axis, velocity):
		return self.axisList[self.axisDict[axis]].setVelocity(velocity)

	def queryVelocity(self, axis):
		return self.axisList[self.axisDict[axis]].readVelocity()

	def setAcceleration(self, axis, acceleration):
		return self.axisList[self.axisDict[axis]].setAcceleration(acceleration)

	def queryAcceleration(self, axis):
		return self.axisList[self.axisDict[axis]].readAcceleration()

	def queryHighLimit(self, axis):
		return self.axisList[self.axisDict[axis]].readHighLimit()

	def setHighLimit(self, axis, highLimit):
		return self.axisList[self.axisDict[axis]].setHighLimit(highLimit)

	def queryLowLimit(self, axis):
		return self.axisList[self.axisDict[axis]].readLowLimit()

	def setLowLimit(self, axis, lowLimit):
		return  self.axisList[self.axisDict[axis]].setLowLimit(lowLimit)

