'''
THIS IS A MEMORY MODULE ON THE SREVER WHICH ACTS LIKE MEMORY OF FILE SYSTEM. ALL THE OPERATIONS REGARDING THE FILE SYSTEM OPERATES IN 
THIS MODULE. THE MODULE HAS POINTER TO DISK AND HAS EXACT SAME LAYOUT AS UNIX TYPE FILE SYSTEM.
'''  
import config, DiskLayout, client_stub, pickle, hashlib

#ORIENTED TO LOWER INTERFACES
sblock = DiskLayout.SuperBlock()
client = client_stub.client_stub()
fail_servers = []	 

#RAID-5 LOGIC
def __ascii_2_str__(b_data):
	data = ''
	for byte in range(len(b_data)/8): data += chr(int(b_data[byte*8: byte*8+8], 2))

	return data


def __str_2_ascii__(string):
	b_data = ''
	for word in string:
		b_data += bin(ord(word) | 0b100000000).replace('0b1', '', 1)
	
	return b_data


def __checksum__(data):
	md5 = hashlib.md5(data)
	retVal = md5.hexdigest()
	checksum_buf = []
	for i in range(0,len(retVal)):
		checksum_buf.append(bin(int(retVal[i],16)).replace('0b','').zfill(4))
	checksum_md5 = ''.join(checksum_buf)
	return checksum_md5


def __raid_block_mapping__(block_number):
	server_sets_size = config.TOTAL_NO_OF_BLOCKS * (4 - 1)		# DATA BLOCKS NUMBER (NOT PARITY BLOCKS)
	server_sets_offset = block_number / server_sets_size
	block_offset = block_number % server_sets_size
	stripe_num = block_offset / 3
	stripe_offset = block_offset % 3
	parity_in_stripe_offset = stripe_num % 4

	server_block_num = stripe_num
	server_id = 8000 + server_sets_offset * 4 + stripe_offset
	if stripe_offset >= parity_in_stripe_offset:
		server_id += 1

	parity_server_id = 8000 + server_sets_offset * 4 + parity_in_stripe_offset
	return [server_id, server_sets_offset, server_block_num, parity_server_id]
	

def __raid_read_block__(block_number):
	# No response from one server, regenerate data from redundancy servers.
	# data is binary
	if block_number >= config.TOTAL_NO_OF_BLOCKS:	return -1
	des_server_id, server_sets_offset, server_block_num, _ = __raid_block_mapping__(block_number)

	if des_server_id not in fail_servers:
		response = client.read(des_server_id, server_block_num*config.BLOCK_SIZE, config.BLOCK_SIZE)
		if response != None: return __ascii_2_str__(response)
		else:	fail_servers.append(des_server_id)

	rec_data = [None for _ in range(3)]
	for server_id in range(server_sets_offset*4, server_sets_offset*4+4):
		server_id += 8000
		if server_id == des_server_id: continue
		if server_id in fail_servers:
			print('FATAL ERROR! MORE THAN TWO RAID DISKS DECAY!')
			quit()
		response = client.read(server_id, server_block_num*config.BLOCK_SIZE, config.BLOCK_SIZE)
		if response == None:
			print('FATAL ERROR! MORE THAN TWO RAID DISKS DECAY!')
			quit()
		else:	rec_data.append(response)

	new_data = rec_data[0] ^ rec_data[1] ^ rec_data[2]
	return new_data

		
def __raid_write_block__(block_number, data):
	# data is binary
	if block_number >= config.TOTAL_NO_OF_BLOCKS or len(data)/8 > config.BLOCK_SIZE:	return -1
	des_server_id, server_sets_offset, server_block_num, parity_server_id = __raid_block_mapping__(block_number)
	fail_count = 0
	parity_data = []
	parity = None
	des = None

	# check servers
	for server_id in range(server_sets_offset*4, server_sets_offset*4+4):
		server_id += 8000
		if server_id in fail_servers:
			parity_data.append(None)
			fail_count += 1
			continue
		response = client.read(server_id, server_block_num*config.BLOCK_SIZE, config.BLOCK_SIZE)
		if response == None:	
			fail_servers.append(server_id)
			parity_data.append(response)
			fail_count += 1
			continue
		if server_id == des_server_id: des = response
		elif server_id == parity_server_id: parity = response
		else:	parity_data.append(response)

	# calculate parity according to failure condition
	if fail_count >= 2:
		print('FATAL ERROR! MORE THAN 2 DISKS FAIL & SYS FAILS!')
		quit()
	elif fail_count == 1:
		if des == None:
			parity = data
			for pdata in parity_data:	parity ^= pdata
		elif parity == None: pass
		else:
			fail_index = parity_data.index(None)
			parity_data.pop(fail_index)
			rec_data = des ^ parity
			for pdata in parity_data:	rec_data ^= pdata		# use old parity to reconstruct bad data
			parity_data.insert(fail_index, rec_data)
			parity = data
			for pdata in parity_data:	parity ^= pdata 		# then use reconstructed data to build new parity
	else:
			parity = data
			for pdata in parity_data: parity ^= pdata
	
	if des != None: 
		response = client.write(des_server_id, server_block_num*config.BLOCK_SIZE, data)
		if response == None:
			fail_servers.append(des_server_id)
			return -1
	
	if parity != None:
		response = client.write(parity_server_id, server_block_num*config.BLOCK_SIZE, parity)
		if response == None:
			fail_servers.append(parity_server_id)


def __initialize__(server_num):
	client.add_proxys(server_num)
	#ALLOCATING BITMAP BLOCKS 0 AND 1 BLOCKS ARE RESERVED FOR BOOT BLOCK AND SUPERBLOCK
	sblock.BITMAP_BLOCKS_OFFSET, count = 2, 2 
	for _ in range(0, sblock.TOTAL_NO_OF_BLOCKS / sblock.BLOCK_SIZE):  	
		bitmap_block = '0' * config.BLOCK_SIZE
		bitmap_block = __str_2_ascii__(bitmap_block)
		__raid_write_block__(count, bitmap_block)
		count += 1
	#ALLOCATING INODE BLOCKS
	sblock.INODE_BLOCKS_OFFSET = count
	for _ in range(0, (sblock.MAX_NUM_INODES * sblock.INODE_SIZE) / sblock.BLOCK_SIZE):		#for Inode blocks
		count  += 1
	#ALLOCATING DATA BLOCKS
	sblock.DATA_BLOCKS_OFFSET = count
	#MAKING BLOCKS BEFORE DATA BLOCKS UNAVAILABLE FOR USE SINCE OCCUPIED BY SUPERBLOCK, BOOTBLOCK, BITMAP AND INODE TABLE
	bitmap_block = '2' * sblock.DATA_BLOCKS_OFFSET
	if len(bitmap_block) % config.BLOCK_SIZE != 0:
		bitmap_block += '0' * (config.BLOCK_SIZE - len(bitmap_block) % config.BLOCK_SIZE)
	for b_blk in range(len(bitmap_block) / config.BLOCK_SIZE):
		__raid_write_block__(2+b_blk, __str_2_ascii__(bitmap_block[b_blk*config.BLOCK_SIZE : (b_blk+1)*config.BLOCK_SIZE]))
	
	
#OPERATIONS ON FILE SYSTEM
class Operations():
	def initialize(self, server_num):
		__initialize__(server_num)


	#RETURNS THE DATA OF THE BLOCK
	def get_data_block(self, block_number):	
		if block_number == 0: print("Memory: Reserved for Boot Block")
		elif block_number == 1: print("Memory: Reserved for Super Block")

		elif block_number >= sblock.BITMAP_BLOCKS_OFFSET and block_number < sblock.INODE_BLOCKS_OFFSET:
			bit_map_blk = list(__ascii_2_str__(__raid_read_block__(block_number)))
			for index in len(bit_map_blk):
				bit = bit_map_blk[index]
				if bit == '2': bit_map_blk[index] = -1
				else: bit_map_blk[index] = int(bit)
			return bit_map_blk
		
		elif block_number >= sblock.INODE_BLOCKS_OFFSET and block_number < sblock.DATA_BLOCKS_OFFSET:
			inode_block = []
			inode_offset = (block_number - sblock.INODE_BLOCKS_OFFSET) * sblock.INODES_PER_BLOCK
			for inode_number in range(inode_offset, inode_offset + sblock.INODES_PER_BLOCK):
				inode_block.append(self.inode_number_to_inode(inode_number))
			return inode_block
		
		elif block_number >= sblock.DATA_BLOCKS_OFFSET and block_number < sblock.TOTAL_NO_OF_BLOCKS:
			return list(__ascii_2_str__(__raid_read_block__(block_number)))
		else: print("Memory: Block index out of range or Wrong input!")

		return -1


	#RETURNS THE BLOCK NUMBER OF AVAIALBLE DATA BLOCK  
	def get_valid_data_block(self):			
		for blk_index in range(sblock.BITMAP_BLOCKS_OFFSET, sblock.INODE_BLOCKS_OFFSET):
			bit_map_blk = list(__ascii_2_str__(__raid_read_block__(blk_index)))
			for bit_index in range(len(bit_map_blk)):
				bit = bit_map_blk[bit_index]
				if bit == '0':
					bit_map_blk[bit_index] = '1'
					bit_map_blk = ''.join(bit_map_blk)
					__raid_write_block__(blk_index, __str_2_ascii__(bit_map_blk))
					return (blk_index*config.BLOCK_SIZE + bit_index)

		print("Memory: No valid blocks available")
		return -1


	#REMOVES THE INVALID DATA BLOCK TO MAKE IT REUSABLE
	def free_data_block(self, block_number): 
		bit_map_blk_num = block_number / config.BLOCK_SIZE
		bit_map_index = block_number % config.BLOCK_SIZE
		bit_map_blk = list(__ascii_2_str__(__raid_read_block__(bit_map_blk_num)))
		bit_map_blk[bit_map_index] = '0'
		bit_map_blk = ''.join(bit_map_blk)
		__raid_write_block__(bit_map_blk_num, __str_2_ascii__(bit_map_blk))

		empty_block = __str_2_ascii__('\0' * config.BLOCK_SIZE)
		__raid_write_block__(block_number, empty_block)


	#WRITES TO THE DATA BLOCK
	def update_data_block(self, block_number, block_data):
		__raid_write_block__(block_number, __str_2_ascii__(block_data))
		print("Memory: Data Copy Completes")
	
	
	#UPDATES INODE TABLE WITH UPDATED INODE
	def update_inode_table(self, inode, inode_number):
		# Need convert array-inode to raw-data
		# If array-inode's size is not full, append \0 (str)
		r_inode = ''
		r_inode += __str_2_ascii__('0'+str(inode[0]))			# type => 2 bytes
		r_inode += bin(int(__str_2_ascii__(inode[1]), 2) | int('1' + '0'*16*8, 2)).replace('0b1', '', 1)				# Name => 16 bytes
		r_inode += bin(inode[2] | 2**(2*8)).replace('0b1', '', 1)			# links num	=> 2 bytes
		r_inode += bin(int(__str_2_ascii__(inode[3]), 2) | int('1' + '0'*19*8, 2)).replace('0b1', '', 1)				# Time created	=> 19 bytes
		r_inode += bin(int(__str_2_ascii__(inode[4]), 2) | int('1' + '0'*19*8, 2)).replace('0b1', '', 1)				# Time accessed	=> 19 bytes
		r_inode += bin(int(__str_2_ascii__(inode[5]), 2) | int('1' + '0'*19*8, 2)).replace('0b1', '', 1)				# Time modified => 19 bytes
		r_inode += bin(inode[6] | 2**(2*8)).replace('0b1', '', 1)			# Inode size => 2 bytes
		if inode[0] == 0:
			for blk in inode[7]:
				if blk == -1:	r_inode += __str_2_ascii__('-1')		# '-1' takes 2 bytes by storing str
				else: r_inode += bin(blk | 2**(2*8)).replace('0b1', '', 1)	# else blk num store true number
		else:
			for entry in inode[7]:
				for word in entry:	r_inode += __str_2_ascii__(word)
		
		if len(r_inode)/8 < config.INODE_SIZE:
			r_inode += __str_2_ascii__('\0'*(config.INODE_SIZE - len(r_inode)/8))

		inode_blk_num = inode_number / sblock.INODES_PER_BLOCK
		inode_offset = inode_number % sblock.INODES_PER_BLOCK
		inode_blk = __raid_read_block__(inode_blk_num)
		inode_blk = inode_blk[: inode_offset*config.INODE_SIZE*8] + r_inode + inode_blk[(inode_offset+1)*config.INODE_SIZE*8 :]
		__raid_write_block__(inode_blk_num, inode_blk)
		# return r_inode

	
	#RETURNS THE INODE FROM INODE NUMBER
	def inode_number_to_inode(self, inode_number):
		inode_blk_num = inode_number / sblock.INODES_PER_BLOCK
		inode_offset = inode_number % sblock.INODES_PER_BLOCK
		r_inode = __raid_read_block__(inode_blk_num)[inode_offset*config.INODE_SIZE*8 : (inode_offset+1)*config.INODE_SIZE*8]
		inode = [None for _ in range(8)]
		count = 0

		if int(r_inode, 2) == 0: return False

		inode[0] = int(__ascii_2_str__(r_inode[:2*8]))
		count += 2*8
		name = bin(int(r_inode[count:count+16*8], 2) | 0).replace('0b', '', 1)
		inode[1] = __ascii_2_str__(name.zfill(len(name)+(8-len(name)%8)))
		count += 16*8
		inode[2] = int(r_inode[count:count+2*8], 2)
		count += 2*8
		inode[3] = __ascii_2_str__(r_inode[count:count+19*8])
		count += 19*8
		inode[4] = __ascii_2_str__(r_inode[count:count+19*8])
		count += 19*8
		inode[5] = __ascii_2_str__(r_inode[count:count+19*8])
		count += 19*8
		inode[6] = int(r_inode[count:count+2*8], 2)
		count += 2*8
		inode[7] = []
		if inode[0] == 0:
			max_data_blocks_allocated = (config.INODE_SIZE - 63 - config.MAX_FILE_NAME_SIZE) / 2
			for _ in range(max_data_blocks_allocated):
				blk = __ascii_2_str__(r_inode[count:count+2*8])
				if blk == '-1': inode[7].append(-1)
				else: inode[7].append(int(r_inode[count:count+2*8], 2))
				count += 2*8
		else:
			entry_size = config.MAX_FILE_NAME_SIZE + len(str(config.MAX_NUM_INODES))
			max_entries = (config.INODE_SIZE - 63 - config.MAX_FILE_NAME_SIZE ) / entry_size
			for _ in range(max_entries):
				entry = __ascii_2_str__(r_inode[count:count+entry_size*8])
				inode[7].append(list(entry))
				count += entry_size * 8
		
		return inode
	

	#SHOWS THE STATUS OF DISK LAYOUT IN MEMORY
	def status(self):
		counter = 1
		string = ""
		string += "\n----------BITMAP: ----------(Block Number : Valid Status)\n"
		block_number = 0
		for i in range(2, sblock.INODE_BLOCKS_OFFSET):
			string += "Bitmap Block : " + str(i - 2) + "\n"
			b = self.get_data_block(i)
			for j in range(0, len(b)):
				if j == 20: break   #only to avoid useless data to print
				string += "\t\t[" + str(block_number + j) + "  :  "  + str(b[j]) + "]  \n"
			block_number += len(b)
			if counter == 1: break
		string += ".....showing just part(20) of 1st bitmap block!\n"

		string += "\n\n----------INODE Blocks: ----------(Inode Number : Inode(Address)\n"
		inode_number = 0
		for i in range(sblock.INODE_BLOCKS_OFFSET, sblock.DATA_BLOCKS_OFFSET):
			string += "Inode Block : " + str(i - sblock.INODE_BLOCKS_OFFSET) + "\n"
			b = self.get_data_block(i)
			for j in range(0, len(b)):
				string += "\t\t[" + str(inode_number + j) + "  :  "  + str(bool(b[j])) + "]  \n"
			inode_number += len(b)
		
		string += "\n\n----------DATA Blocks: ----------\n  "
		counter = 0
		for i in range(sblock.DATA_BLOCKS_OFFSET, sblock.TOTAL_NO_OF_BLOCKS):
			if counter == 25: 
				string += "......Showing just part(25) data blocks\n"
				break
			string += (str(i) + " : " + "".join(self.get_data_block(i))) + "  "
			counter += 1

		
		string += "\n\n----------HIERARCHY: ------------\n"
		for i in range(sblock.INODE_BLOCKS_OFFSET, sblock.DATA_BLOCKS_OFFSET):
			for j in range(0, sblock.INODES_PER_BLOCK):
				inode = self.get_data_block(i)[j]
				if inode and inode[0]:
					string += "\nDIRECTORY: " + inode[1] + "\n"
					for x in inode[7]: string += "".join(x[:config.MAX_FILE_NAME_SIZE]) + " || "
					string += "\n"
		
		return string


if __name__ == '__main__':
	# sblock = DiskLayout.SuperBlock()
	# sblock = pickle.dumps(sblock)
	# print len(sblock)
	# b_sblock = ''
	# for byte in sblock:
	# 	ascii_code = bin(ord(byte) | 0b100000000).replace('0b1', '', 1)
	# 	print ascii_code
	# 	print bin(ascii_code | 0b100000000) + ' ' + byte
  #   ascii_code = ascii_code.replace('0b', '0', 1)
  #   b_sblock += ascii_code	
	
	# print len(sblock)

	# for num in range(12):
	# 	print __raid_block_mapping__(num), ' ', num

	# string = 'abc'
	# print __ascii_2_str__(__str_2_ascii__(string))
	# print type(__str_2_ascii__(string))

	# print int(__ascii_2_str__(__str_2_ascii__('0'+ str('1'))))
	# print len(bin(int(__str_2_ascii__(str(1)), 2) | int('1' + '0'*2*8, 2)).replace('0b1', '', 1)) / 8

	# t_inode = InodeOps.Table_Inode(0)
	# t_inode.name = 'AA'
	# t_inode.blk_numbers[0] = 19
	# t_inode.size = 4485
	# t_inode.time_accessed = str(datetime.datetime.now())[:19]
	# t_inode.time_created = str(datetime.datetime.now())[:19]
	# t_inode.time_modified = str(datetime.datetime.now())[:19]
	# t_inode.directory = {'1.txt': 20}

	# iop = InodeOps.InodeOperations()
	# a_inode = iop.convert_table_to_array(t_inode)

	# op = Operations()
	# temp = op.update_inode_table(a_inode, 1)
	# print a_inode
	# print
	# print a_inode == op.inode_number_to_inode(1, temp)
	pass