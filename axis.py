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
			accelDuration = (self.velocity - self.baseVelocity) / self.acceleration
			acclDistance = 0.5 * (self.velocity - self.baseVelocity) * accelDuration
			moveDistance = self.targetPosition - self.lastPosition
			constVelDuration = (moveDistance - 2 * acclDistance) / self.velocity
			decelStartTime = accelDuration + constVelDuration
			totalMoveDuration = 2 * accelDuration + constVelDuration

			movingTimeDelta = currentTime - self.moveStartTime
			movingTimeSeconds = movingTimeDelta.total_seconds()

			self.currentPosition = self.lastPosition + self.baseVelocity * movingTimeSeconds
			### calculate current position
			if movingTimeSeconds < accelDuration:
				# accelerating
				self.currentPosition += 0.5 * self.acceleration * movingTimeSeconds * movingTimeSeconds
			else:
				# past the point of accelerating
				self.currentPosition += 0.5 * self.acceleration * accelDuration

				if movingTimeSeconds < decelStartTime:
					# moving with constant speed
					self.currentPosition += self.velocity * (movingTimeSeconds - accelDuration)
				else:
					# past the point of moving with constant speed
					self.currentPosition += self.velocity * constVelDuration

					if movingTimeSeconds < totalMoveDuration:
						# decelerating
						self.currentPosition += (self.velocity - 0.5 * self.acceleration * (movingTimeSeconds - decelStartTime)) * (movingTimeSeconds - decelStartTime)
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

