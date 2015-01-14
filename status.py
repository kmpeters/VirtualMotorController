#!/usr/bin/env python

class Status:
	'''
	Class representing axis status
	'''
	def __init__(self):
		# 
		self.direction = 1
		#
		self.doneMoving = 1
		self.moving = 0
		# 
		self.highLimitActive = 0
		self.lowLimitActive = 0
		#
		self.homing = 0
		self.homed = 0
		self.homeSwitchActive = 0
		#
		self.error = False
		self.errorMessage = None

		# Bit definitions
		self.DIRECTION = 1 << 0
		self.DONE_MOVING = 1 << 1
		self.MOVING = 1 << 2
		self.HIGH_LIMIT = 1 << 3
		self.LOW_LIMIT = 1 << 4
		self.HOMING = 1 >> 5
		self.HOME_LIMIT = 1 << 6
		self.HOMED = 1 << 7
		self.ERROR = 1 << 8

		#
		self.status = 0
		self.calcStatus()

	def setError(self, flag, message):
		self.error = flag
		self.errorMessage = message
		if self.error:
			self.status |= self.ERROR
		else:
			self.status &= ~self.ERROR

	def setMoving(self):
		self.doneMoving = 0
		self.moving = 1
		self.status |= self.MOVING
		self.status &= ~self.DONE_MOVING

	def setDoneMoving(self):
		self.doneMoving = 1
		self.moving = 0
		self.status |= self.DONE_MOVING
		self.status &= ~self.MOVING

	def setDirPositive(self):
		self.direction = 1
		self.status |= self.DIRECTION

	def setDirNegative(self):
		self.direction = 0
		self.status &= ~self.DIRECTION

	def getStatus(self):
		return self.status

	def calcStatus(self):
		status = 0
		if self.direction:
			status |= self.DIRECTION
		if self.doneMoving:
			status |= self.DONE_MOVING
		if self.moving:
			status |= self.MOVING
		if self.highLimitActive:
			status |= self.HIGH_LIMIT
		if self.lowLimitActive:
			status |= self.LOW_LIMIT
		if self.homing:
			status |= self.HOMING
		if self.homeSwitchActive:
			status |= self.HOME_LIMIT
		if self.homed:
			status |= self.HOMED
		if self.error:
			status |= self.ERROR
		self.status = status
		return
