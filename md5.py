import hashlib
def __ckecksum__(data):
	md5 = hashlib.md5(data)
	retVal = md5.hexdigest()
	checksum_buf = []
	for i in range(0,len(retVal)):
		checksum_buf.append(bin(int(retVal[i],16)).replace('0b','').zfill(4))
	checksum_md5 = ''.join(checksum_buf)
	return checksum_md5


if __name__ == '__main__':
	# a = '0' * 496 * 8
	# a += __ckecksum__(a)
	# print len(a[-16*8:]) / 8
	print __ckecksum__(None)
