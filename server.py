#!/usr/bin/env python

import controller

import os
import sys
import getopt
import asynchat
import asyncore
import socket

DEFAULT_PORT = 31337

class ConnectionDispatcher(asyncore.dispatcher):
	def __init__(self, port):
		asyncore.dispatcher.__init__(self)
		self.port = port
		self.device = controller.Controller()
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

		# Display received commands
		#!print request

		# Commands of form
		# X MV 400
		response = self.device.handleCommand(request)

		if response != None:
			self.sendClientResponse("%s" % response)

		return

	def sendClientResponse(self, response=""):
		data = response + self.outputTerminator
		self.push(data)


def getProgramName(args=None):
	if args == None:
		args = sys.argv
	if len(args) == 0 or args[0] == "-c":
		return "PROGRAM_NAME"
	return os.path.basename(args[0])


def printUsage():
	print """\
Usage: %s [-ph]

Options:
  -p,--port=NUMBER   Listen on the specified port NUMBER for incoming
                     connections (default: %d)
  -h,--help          Print usage message and exit\
""" % (getProgramName(), DEFAULT_PORT)


def parseCommandLineArgs(args):
	(options, extra) = getopt.getopt(args[1:], "p:h", ["port=", "help"])

	port = DEFAULT_PORT

	for eachOptName, eachOptValue in options:
		if eachOptName in ("-p", "--port"):
			port = int(eachOptValue)
		elif eachOptName in ("-h", "--help"):
			printUsage()
			sys.exit(0)

	if len(extra) > 0:
		print "Error: unexpected command-line argument \"%s\"" % extra[0]
		printUsage()
		sys.exit(1)

	return port


def main(args):
	port = parseCommandLineArgs(args)
	server = ConnectionDispatcher(port)
	try:
		asyncore.loop()
	except KeyboardInterrupt:
		print
		print "Shutting down the server..."
		sys.exit(0)


if __name__ == '__main__':
	# Check the python version
	if sys.version_info < (2,7,0):
		sys.stderr.write("You need Python 2.7 or later to run this script\n")
		raw_input("Press enter to quit... ")
		sys.exit(1)

	# Try to run the server
	try:
		main(sys.argv)
	except Exception, e:
		if isinstance(e, SystemExit):
			raise e
		else:
			print "Error: %s" % e
			sys.exit(1)
