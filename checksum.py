def __checksum__(data):
	str_buf = []
	for i in range(0, len(data), 8):
		str_buf.append(int(data[i: i + 8], 2))
	#print str_buf
	string = bytearray(str_buf)
	#print(data)
	crc = 0xFFFF
	for pos in string:
		crc ^= pos
		for i in range(8):
			if ((crc & 1) != 0):
				crc >>= 1
				crc ^= 0xA001
			else:
				crc >>= 1
	#print hex(((crc & 0xff) << 8) + (crc >> 8))
	string = hex(((crc & 0xff) << 8) + (crc >> 8))
	checksum_buf = []
	for i in range(0,4):
		checksum_buf.append(bin(int(string[i+2],16)).replace('0b','').zfill(4))
	checksum_crc16 = ''.join(checksum_buf)
	#print ret_Val
	return checksum_crc16


if __name__ == '__main__':
	data = bin(ord('a') | 0b100000000).replace('0b1', '', 1)
	data = data * 510
	print len(__checksum__(data))