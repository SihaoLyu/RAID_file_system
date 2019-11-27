# SKELETON CODE FOR CLIENT STUB HW4
import xmlrpclib, config, pickle, os, random

class client_stub():
	proxys = []
	proxys_num = 0
	raid_mode = -1

	def set_raid_mode(self,raid_mode):
		self.raid_mode = raid_mode

	
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
				data = self.proxys[server_id-8000].read(offset, length)
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
				msg = self.proxys[server_id-8000].write(offset, data)
				break
			except Exception as err:
				print(err.args)

		if msg == None:	print("RPC write error!")
		return msg

	def CorruptData(self, server_id):
		#corrupt_blk = random.randint(0,config.TOTAL_NO_OF_BLOCKS)
		corrupt_blk = random.randint(0,4)
		corrupt_bit = random.randint(0,config.WHOLE_BLOCK_SIZE)
		data = self.read(server_id + 8000, corrupt_blk * config.WHOLE_BLOCK_SIZE, config.WHOLE_BLOCK_SIZE)
		if not data:
			print('CORRUPTED DATA BLOCK LANDED ON BAD SERVER')
			return 
		if data[corrupt_bit] == '1' :
			data = data[0:corrupt_bit] + '0' + data[corrupt_bit + 1: ]
			pass
		elif data[corrupt_bit] == '0' :
			data = data[0:corrupt_bit] + '1' + data[corrupt_bit + 1: ]
			pass
		else:
			pass
		self.write(server_id + 8000, corrupt_blk * config.WHOLE_BLOCK_SIZE, data)

if __name__ == '__main__':
	for i in range(4):
		os.system('gnome-terminal -e \"python server_stub.py ' + str(8000+i) + '\"')

	client = client_stub()
	client.add_proxys(4)
	client.write(8000, 0, '1010'*2)
	print client.read(8000, 0, 1)
	client.CorruptData(8000)
	a = client.read(8000, 0, 2048)
	print a.find('1',7)
