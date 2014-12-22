#!/usr/bin/env python

import axis
import time

class Controller:
	'''
	Class representing a motor controller

	'''
	def __init__(self):
		self.numAxes = 1
		self.axisList = []
		self.enforceLimits = False

		for i in range(self.numAxes):
			self.axisList.append( axis.Axis() )

	def queryPosition():
		pass

	def queryStatus():
		pass

if __name__ == '__main__':
	myc = Controller()
	myc.axisList[0].move(5.0)
	for i in range(100):
		print myc.axisList[0].readPosition()
		time.sleep(0.1)

