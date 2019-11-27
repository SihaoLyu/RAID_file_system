# SKELETON CODE FOR SERVER STUB HW4
import xmlrpclib, sys, os
from SimpleXMLRPCServer import SimpleXMLRPCServer

import pickle , Disk

disk = Disk.disk()

# FUNCTION DEFINITIONS 
def read(offset, length):
	offset = pickle.loads(offset)
	length = pickle.loads(length)
	return disk.read(offset, length)


def write(offset, data):
	offset = pickle.loads(offset)
	data = pickle.loads(data)
	return disk.write(offset, data)

port = int(sys.argv[1])
server = SimpleXMLRPCServer(("localhost", port))
print("Listening on port " + str(port) + "....")

server.register_function(read, "read")
server.register_function(write, "write")
server.serve_forever()


if __name__ == '__main__':
	# port = input("Type in port number: ")
	# server = SimpleXMLRPCServer(("", port))
	# print("Listening on port " + str(port) + "....")

	# server.register_function(read, "read")
	# server.register_function(write, "write")

	# server.serve_forever()	
	pass













