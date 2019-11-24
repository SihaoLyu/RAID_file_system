# SKELETON CODE FOR CLIENT STUB HW4
import xmlrpclib, config, pickle

class client_stub():
	proxys = []
	proxys_num = 0

	def add_proxys(self, server_num):
		for num in range(server_num):
			port = 8000 + num
			URL = r"http://localhost:" + str(port) + r"/"
			self.proxys.append(xmlrpclib.ServerProxy(URL))
			self.proxys_num += 1


	def read(self, server_id, offset, length):
		offset = pickle.dumps(offset)
		length = pickle.dumps(length)
		data = None
		for _ in range(3):
			try:
				data = self.proxys[server_id].read(offset, length)
				break
			except Exception as err:
				print(err.args)

		return data


	def write(self, server_id, offset, data):
		offset = pickle.dumps(offset)
		data = pickle.dumps(data)
		msg = None
		for _ in range(3):
			try:
				msg = self.proxys[server_id].write(offset, data)
				break
			except Exception as err:
				print(err.args)

		if msg == None:	print("RPC write error!")
		return msg


if __name__ == '__main__':
	c = client_stub()
	c.add_proxys(4)
	print c.proxys