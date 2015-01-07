#!/usr/bin/env python

import status
import datetime

class Axis:
	'''
	Class representing a motor axis

	'''
	def __init__(self):
		# units / second
		self.velocity = 400
		self.baseVelocity = 0
		# units / second / second
		self.acceleration = 400
		#
		self.highLimit = 40000
		self.lowLimit = -40000
		#
		self.units = "counts"
		self.resolution = 1.0
		#
		self.moveStartTime = None
		self.abortTime = None
		self.lastPosition = 0
		self.currentPosition = 0
		self.targetPosition = 0
		# Move info
		self.accelDuration = 0.0
		self.accelDistance = 0
		self.moveDistance = 0
		self.constVelDuration = 0.0
		self.decelStartTime = 0.0
		self.totalMoveDuration = 0.0
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
			self.targetPosition = int(round(targetPosition)
			# Calculate values needed for readback position calculation
			self.accelDuration = (self.velocity - self.baseVelocity) / self.acceleration
			self.accelDistance = 0.5 * (self.velocity - self.baseVelocity) * self.accelDuration
			self.moveDistance = abs(self.targetPosition - self.lastPosition)
			self.constVelDuration = (self.moveDistance - 2 * self.accelDistance) / self.velocity
			self.decelStartTime = self.accelDuration + self.constVelDuration
			self.totalMoveDuration = 2 * self.accelDuration + self.constVelDuration

			print "Start Pos:", self.lastPosition, self.units
			print "End Pos:", self.targetPosition, self.units
			print "Move Distance:", self.moveDistance, self.units
			print "Move Duration:", self.totalMoveDuration, "seconds"
			print "Accel Duration:", self.accelDuration, "seconds"
			print "Accel Distance:", self.accelDistance, self.units
			print "Constant Vel Duration:", self.constVelDuration, "seconds"
			print "Decel Start Time:", self.decelStartTime, "seconds"

		return "OK"

	def stop(self):
		self.abortTime = datetime.datetime.now()
		return "OK"

	def readPosition(self):
		if self.moveStartTime == None:
			# axis isn't moving
			# should stuff be reset here?
			pass
		else:
			# axis is moving
			currentTime = datetime.datetime.now()

			# calculate moving times
			movingTimeDelta = currentTime - self.moveStartTime
			movingTimeSeconds = movingTimeDelta.total_seconds()

			# This only works (badly) for moves in the positive direction.  There is still overshoot
			self.currentPosition = self.lastPosition + self.baseVelocity * movingTimeSeconds
			### calculate current position
			if movingTimeSeconds < self.accelDuration:
				# accelerating
				self.currentPosition += 0.5 * self.acceleration * movingTimeSeconds * movingTimeSeconds
			else:
				# past the point of accelerating
				self.currentPosition += 0.5 * self.acceleration * self.accelDuration

				if movingTimeSeconds < self.decelStartTime:
					# moving with constant speed
					self.currentPosition += self.velocity * (movingTimeSeconds - self.accelDuration)
				else:
					# past the point of moving with constant speed
					self.currentPosition += self.velocity * self.constVelDuration

					if movingTimeSeconds < self.totalMoveDuration:
						# decelerating
						self.currentPosition += (self.velocity - 0.5 * self.acceleration * (movingTimeSeconds - self.decelStartTime)) * (movingTimeSeconds - self.decelStartTime)
					else:
						# move is done
						self.currentPosition = self.targetPosition
						self.lastPosition = self.targetPosition
						self.moveStartTime = None

		return int(round(self.currentPosition))

	def setPosition(self):
		return

	# Does it make more sense to have an updateController() method that is called before each readStatus and readPosition call?

	def readStatus(self):
		# Update moving status
		if self.moveStartTime == None:
			self.status.setDoneMoving()
		else:
			# axis might still be moving
			currentTime = datetime.datetime.now()

			# calculate moving times
			movingTimeDelta = currentTime - self.moveStartTime
			movingTimeSeconds = movingTimeDelta.total_seconds()

			if movingTimeSeconds < self.totalMoveDuration:
				# move is in progress
				self.status.setMoving()
			else:
				# move is done but neither position or status have been updated
				self.status.setDoneMoving()

		return self.status.doneMoving

	def setVelocity(self, velocity):
		self.velocity = velocity
		return "OK"

	def readVelocity(self):
		return self.velocity

	def setAcceleration(self, acceleration):
		self.acceleration = acceleration
		return "OK"

	def readAcceleration(self):
		return self.acceleration

	def readHighLimit(self):
		return self.highLimit

	def setHighLimit(self, highLimit):
		self.highLimit = int(round(highLimit))
		return "OK"

	def readLowLimit(self):
		return self.lowLimit

	def setLowLimit(self, lowLimit):
		self.lowLimit = int(round(lowLimit))
		return  "OK"

