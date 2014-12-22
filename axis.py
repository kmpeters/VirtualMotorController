#!/usr/bin/env python

import status
import datetime

class Axis:
	'''
	Class representing a motor axis

	'''
	def __init__(self):
		# units / second
		self.velocity = 1.0
		self.baseVelocity = 0.0
		# units / second / second
		self.acceleration = 1.0
		#
		self.highLimit = 100.0
		self.lowLimit = 100.0
		#
		self.units = "counts"
		self.resolution = 1.0
		#
		self.moveStartTime = None
		self.lastPosition = 0.0
		self.currentPosition = 0.0
		self.targetPosition = 0.0
		#
		self.enforceLimits = False
		#
		self.status = status.Status()
	
	def move(self, targetPosition):
		self.lastPosition = self.currentPosition
		# how to detect if controller has limits enabled?
		if (self.enforceLimits == True) and (targetPosition > self.highLimit):
			self.status.setError(True, "Target position exceeds high limit")
		elif (self.enforceLimits == True) and (targetPosition < self.lowLimit):
			self.status.setError(True, "Target position exceeds low limit")
		else:
			#
			self.moveStartTime = datetime.datetime.now()
			self.targetPosition = targetPosition
		return

	def readPosition(self):
		if self.moveStartTime == None:
			# axis isn't moving
			pass
		else:
			# axis is moving
			currentTime = datetime.datetime.now()

			# calculate moving times
			accelerationTime = (self.velocity - self.baseVelocity) / self.acceleration
			accelerationDistance = 0.5 * (self.velocity - self.baseVelocity) * accelerationTime
			moveDistance = self.targetPosition - self.lastPosition
			constantVelTime = (moveDistance - 2 * accelerationDistance) / self.velocity
			accelAndVelTime = accelerationTime + constantVelTime
			totalMoveTime = 2 * accelerationTime + constantVelTime

			movingTimeDelta = currentTime - self.moveStartTime
			movingTimeSeconds = movingTimeDelta.total_seconds()
			accelTimeEnd = accelerationTime
			constVelTimeEnd = accelAndVelTime
			decelTimeEnd = totalMoveTime

			### calculate current position
			if movingTimeSeconds < accelTimeEnd:
				# accelerating
				self.currentPosition = self.lastPosition + self.baseVelocity * movingTimeSeconds + 0.5 * self.acceleration * movingTimeSeconds * movingTimeSeconds
			elif movingTimeSeconds < constVelTimeEnd:
				# moving at constant speed
				self.currentPosition = self.lastPosition + self.baseVelocity * movingTimeSeconds + 0.5 * self.velocity * accelerationTime + (movingTimeSeconds - accelTimeEnd) * self.velocity
			elif movingTimeSeconds < decelTimeEnd:
				# decelerating
				self.currentPosition = self.lastPosition + self.baseVelocity * movingTimeSeconds + 0.5 * self.velocity * accelerationTime + self.velocity * constantVelTime + (self.velocity - 0.5 * self.acceleration * (movingTimeSeconds - decelTimeEnd)) * (movingTimeSeconds - decelTimeEnd)
			else:
				# move is done
				self.currentPosition = self.targetPosition
				self.lastPosition = self.targetPosition


		return self.currentPosition

	def setPosition(self):
		return

	def readStatus(self):
		return

	def setVelocity(self, velocity):
		self.velocity = velocity
		return

	def readVelocity(self):
		return self.velocity

	def setAcceleration(self, acceleration):
		self.acceleration = acceleration
		return

	def readAcceleration(self):
		return self.acceleration

	def readHighLimit(self):
		return self.highLimit

	def setHighLimit(self, highLimit):
		self.highLimit = highLimit
		return

	def readLowLimit(self):
		return self.lowLimit

	def setLowLimit(self, lowLimit):
		self.lowLimit = lowLimit
		return 

