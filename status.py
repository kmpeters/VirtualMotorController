#!/usr/bin/env python

class Status:
	'''
	Class representing axis status
	'''
	def __init__(self):
		# 
		self.direction = 0
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
		self.error = True
		self.errorMessage = None

	def setError(self, flag, message):
		self.error = flag
		slef.errorMessage = message

	def setMoving(self):
		self.doneMoving = 0
		self.moving = 1

	def setDoneMoving(self):
		self.doneMoving = 1
		self.moving = 0

