def calc_crc(str_buf):
    data = bytearray(str_buf)
    #print(data)
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    #print hex(((crc & 0xff) << 8) + (crc >> 8))
    return hex(((crc & 0xff) << 8) + (crc >> 8))


def checksum(data):
	str_buf = []
	for i in range(0, len(data), 8):
		str_buf.append(int(data[i: i + 8], 2))
	#print str_buf
	ret_Val = calc_crc(str_buf)
	checksum_buf = []
	for i in range(0,4):
		checksum_buf.append(bin(int(ret_Val[i+2],16)).replace('0b','').zfill(4))
	checksum_crc16 = ''.join(checksum_buf)
	#print ret_Val
	return checksum_crc16

if __name__ == "__main__":
	print(checksum('10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'))
#if __name__ == "__main__":
	#crc = calc_crc('0102030405060708')



