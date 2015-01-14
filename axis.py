#!/usr/bin/env python

import status
import datetime
import math

class Axis:
	'''
	Class representing a motor axis

	'''
	def __init__(self, index):
		self.index = index
		# units / second
		self.velocity = 400
		self.baseVelocity = 0
		# units / second / second
		self.acceleration = 400
		self.deceleration = 400
		#
		self.highLimit = 40000
		self.lowLimit = -40000
		#
		self.units = "counts"
		self.resolution = 1.0
		#
		self.moveStartTime = None
		self.abortTime = None
		#
		self.lastPosition = 0
		self.currentPosition = 0
		self.currentDisplacement = 0
		self.targetPosition = 0
		self.direction = 1
		self.moveVelocity = self.velocity
		# Move info
		self.accelDuration = 0.0
		self.accelDistance = 0
		self.decelDuration = 0.0
		self.decelDistance = 0
		self.moveDistance = 0
		self.constVelDuration = 0.0
		self.decelStartTime = 0.0
		self.moveDuration = 0.0
		#
		self.enforceLimits = False
		#
		self.status = status.Status()
	
	def move(self, targetPosition):
		if self.moveStartTime != None:
			# Ignore moves while a move is in progress
			return "Busy"

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
			
			# |
			# |
			# |      _________
			# |     /         \
			# |    /           \
			# |   /             \
			# L__|_______________|__
			#

			# Calculate direction
			if self.targetPosition < self.lastPosition:
				# Move is negative
				self.direction = -1
				self.status.setDirNegative()
			else:
				# Move is positive
				self.direction = 1
				self.status.setDirPositive()
			
			# Calculate values needed for readback position calculation
			self.moveDistance = abs(self.targetPosition - self.lastPosition)

			self.accelDuration = (self.velocity - self.baseVelocity) / self.acceleration
			self.accelDistance = 0.5 * (self.velocity - self.baseVelocity) * self.accelDuration + self.baseVelocity * self.accelDuration

			self.decelDuration = (self.velocity - self.baseVelocity) / self.deceleration
			self.decelDistance = 0.5 * (self.velocity - self.baseVelocity) * self.decelDuration + self.baseVelocity * self.decelDuration

			if self.moveDistance < (self.accelDistance + self.decelDistance):
				# Desired speed is never reached
				peakVelocity = math.sqrt( 2 * self.acceleration * self.deceleration * self.moveDistance / (self.acceleration + self.deceleration) )
				print "+---------"
				print "peakVelocity =", peakVelocity
				self.moveVelocity = peakVelocity

				# Recalculate values
				self.accelDuration = peakVelocity / self.acceleration
				self.accelDistance = 0.5 * peakVelocity * self.accelDuration

				self.decelDuration = (peakVelocity - self.baseVelocity) / self.deceleration
				self.decelDistance = 0.5 * (peakVelocity - self.baseVelocity) * self.decelDuration + self.baseVelocity * self.decelDuration

				self.constVelDuration = 0.0
			else:
				self.moveVelocity = self.velocity
				self.constVelDuration = (self.moveDistance - self.accelDistance - self.decelDistance) / self.velocity

			self.decelStartTime = self.accelDuration + self.constVelDuration
			self.moveDuration = self.decelStartTime + self.decelDuration

			print "+--------- motor", (self.index + 1)
			print "Start Pos:", self.lastPosition, self.units
			print "End Pos:", self.targetPosition, self.units
			print "Move Distance:", self.moveDistance, self.units
			print "Move Duration:", self.moveDuration, "seconds"
			print
			print "Accel Duration:", self.accelDuration, "seconds"
			print "Accel Distance:", self.accelDistance, self.units
			print
			print "Constant Vel Duration:", self.constVelDuration, "seconds"
			print "Decel Start Time:", self.decelStartTime, "seconds"
			print
			print "Decel Duration:", self.decelDuration, "seconds"
			print "Decel Distance:", self.decelDistance, self.units
			print

		return "OK"


	def moveRelative(self, displacement):
		if self.moveStartTime != None:
			# Ignore moves while a move is in progress
			return "Busy"

		targetPosition = self.lastPosition + displacement
		retval = self.move(targetPosition)

		return retval


	def jog(self, velocity):
		#!print "velocity", velocity

		# Simulate jogging by issuing an hour-long move
		displacement = velocity * 3600.0
		retval = self.moveRelative(displacement)

		return retval


	def stop(self):
		if self.moveStartTime == None:
			# motor isn't currently moving
			self.abortTime = None
		else:
			if self.abortTime != None:
				# a stop is already in progress, do nothing
				pass
			else:
				# motor is moving, this is the first stop request
				self.abortTime = datetime.datetime.now()
				abortTimeDelta = self.abortTime - self.moveStartTime
				abortTimeSeconds = abortTimeDelta.total_seconds()

				# Recalculate the motion profile
				if abortTimeSeconds < self.accelDuration:
					# stop received while accelerating
					self.accelDuration = abortTimeSeconds
					self.accelDistance = 0.5 * self.acceleration * abortTimeSeconds ** 2 + self.baseVelocity * abortTimeSeconds

					peakVelocity = self.acceleration * abortTimeSeconds + self.baseVelocity

					self.constVelDuration = 0.0

					self.decelStartTime = abortTimeSeconds

					self.decelDuration = (peakVelocity - self.baseVelocity) / self.deceleration
					self.decelDistance = 0.5 * (peakVelocity - self.baseVelocity) * self.decelDuration + self.baseVelocity * self.decelDuration

					self.moveDistance = self.accelDistance + self.decelDistance
					self.moveDuration = self.accelDuration + self.decelDuration

					self.moveVelocity = peakVelocity
				elif abortTimeSeconds < self.decelStartTime:
					# stop received while moving with constant velocity
					self.decelStartTime = abortTimeSeconds

					self.constVelDuration = abortTimeSeconds - self.accelDuration

					self.moveDistance = self.accelDistance + self.moveVelocity * self.constVelDuration + self.decelDistance
					self.moveDuration = self.accelDuration + self.constVelDuration + self.decelDuration

				elif abortTimeSeconds < self.moveDuration:
					# stop received while decelerating, do nothing
					pass
				else:
					print "Error: Stop received after a move should have been complete."

		return "OK"

	def readPosition(self):
		if self.moveStartTime == None:
			# axis isn't moving
			# should stuff be reset here?
			pass
		else:
			moveFlag = True

			# axis is moving
			currentTime = datetime.datetime.now()

			# calculate moving times
			movingTimeDelta = currentTime - self.moveStartTime
			movingTimeSeconds = movingTimeDelta.total_seconds()

			### calculate current position
			self.currentDisplacement = self.baseVelocity * movingTimeSeconds

			if movingTimeSeconds < self.accelDuration:
				# accelerating
				self.currentDisplacement += 0.5 * self.acceleration * movingTimeSeconds * movingTimeSeconds
			else:
				# past the point of accelerating
				self.currentDisplacement += 0.5 * (self.moveVelocity - self.baseVelocity) * self.accelDuration

				if movingTimeSeconds < self.decelStartTime:
					# moving with constant speed, will never be true for short moves
					self.currentDisplacement += (self.moveVelocity - self.baseVelocity) * (movingTimeSeconds - self.accelDuration)
				else:
					# past the point of moving with constant speed, constant speed component will be zero for short moves
					self.currentDisplacement += (self.moveVelocity - self.baseVelocity) * self.constVelDuration

					if movingTimeSeconds < self.moveDuration:
						# decelerating
						self.currentDisplacement += ((self.moveVelocity - self.baseVelocity) - 0.5 * self.deceleration * (movingTimeSeconds - self.decelStartTime)) * (movingTimeSeconds - self.decelStartTime)
					else:
						# move is done
						moveFlag = False

			if moveFlag == True:
				self.currentPosition = self.lastPosition + self.direction * self.currentDisplacement
			else:
				if self.abortTime == None:
					self.currentPosition = self.targetPosition
				else:
					self.currentPosition = self.lastPosition + self.direction * self.moveDistance
					self.abortTime = None
				self.lastPosition = self.currentPosition
				self.moveStartTime = None
		
		# tdir/overshoot debugging
		#!if (self.direction == 1 and self.currentPosition > self.targetPosition) or (self.direction == -1 and self.currentPosition < self.targetPosition):
		#!	print
		#!	print "Overshoot"
		#!	print
		#!	print "direction", self.direction
		#!	print "current pos", self.currentPosition
		#!	print "target pos", self.targetPosition
		#!	print 
		#!	print "elapsed time", movingTimeSeconds
		#!	print "expected time", self.moveDuration

		return self.currentPosition

	def setPosition(self, newPosition):
		if self.moveStartTime == None:
			# Axis isn't moving, redefine the position
			self.currentPosition = newPosition
			self.lastPosition = self.currentPosition
		else:
			# Move is in progress, do nothing
			pass
		return "OK"

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

			if movingTimeSeconds < self.moveDuration:
				# move is in progress
				self.status.setMoving()
			else:
				# move is done but neither position or status have been updated
				self.status.setDoneMoving()

		return self.status.getStatus()

	def setVelocity(self, velocity):
		# velocity is negative when jogging, but all position calculations require positive velocities
		self.velocity = abs(velocity)
		return "OK"

	def readVelocity(self):
		return self.velocity

	def setBaseVelocity(self, velocity):
		self.baseVelocity = velocity
		return "OK"

	def readBaseVelocity(self):
		return self.baseVelocity

	def setAcceleration(self, acceleration):
		self.acceleration = acceleration
		self.deceleration = acceleration
		return "OK"

	def readAcceleration(self):
		return self.acceleration

	def readHighLimit(self):
		return self.highLimit

	def setHighLimit(self, highLimit):
		self.highLimit = highLimit
		return "OK"

	def readLowLimit(self):
		return self.lowLimit

	def setLowLimit(self, lowLimit):
		self.lowLimit = lowLimit
		return  "OK"

