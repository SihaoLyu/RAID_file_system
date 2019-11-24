import random
#not block but byte
def CorruptData(self, server_id):
	corrupt_blk = random.randint(0,config.TOTAL_NO_OF_BLOCKS)
	corrupt_bit = random.randint(0,config.BLOCK_SIZE)
	data = self.read(server_id, corrupt_blk * config.BLOCK_SIZE, config.BLOCK_SIZE) 
	if data[corrupt_bit] == 1 :
		data[corrupt_bit] = 0
	elif data[corrupt_bit] == 0 :
		data[corrupt_bit] = 1
	else:
		pass
	self.write(server_id, corrupt_blk * config.BLOCK_SIZE, data)



