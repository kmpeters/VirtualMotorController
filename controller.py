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
		self.axisDict = {}
		self.axisList = []
		self.enforceLimits = False

		for i in range(self.numAxes):
			self.axisList.append( axis.Axis() )
			self.axisDict[self.axisNameList[i]] = i

	def queryPosition(self, axis):
		return self.axisList[self.axisDict[axis]].readPosition()

	def queryStatus(self, axis):
		return self.axisList[self.axisDict[axis]].readStatus()


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
		self.outputTerminator = ";\r\n"
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

		self.sendClientResponse("%s received" % request)
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

	d = ConnectionDispatcher(port)
	asyncore.loop()
