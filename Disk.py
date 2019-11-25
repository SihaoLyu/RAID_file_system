import config

class disk():
  TOTAL_NO_OF_BLOCKS = config.TOTAL_NO_OF_BLOCKS
  BLOCK_SIZE = config.BLOCK_SIZE  # bytes
  WHOLE_BLOCK_SIZE = config.WHOLE_BLOCK_SIZE
  DISK_SIZE = config.TOTAL_NO_OF_BLOCKS * config.WHOLE_BLOCK_SIZE
  TRACK = ""

  def __init__(self):
    self.TRACK += "0" * (self.DISK_SIZE * 8)


  def read(self, offset, length):
    # offset is byte 
    if offset < 0 or offset > self.DISK_SIZE:
      print("Bad read offset from server!")
      return -1

    if length < 0:
      print("Bad read length!")
      return -1

    if offset + length > self.DISK_SIZE:
      print("Read length exceeds disk boundary!")
      return -1

    data = self.TRACK[offset*8 : offset*8 + length*8]
    return data


  def write(self, offset, data):
    # offset is byte, data is binary
    if offset < 0 or offset > self.DISK_SIZE:
      print("Bad write offset from server!")
      return -1

    if len(data) % 8 != 0:
      print ('Data does not align with bytes!')
      return -1

    if offset + len(data)/8 > self.DISK_SIZE:
      print("Write length exceeds disk boundary!")
      return -1

    self.TRACK = self.TRACK[0:offset*8] + data + self.TRACK[offset*8 + len(data):]
    return 1


if __name__ == '__main__':
  a = disk()
  data = 'ab'
  b_data = ''
  for byte in data:
    ascii_code = bin(ord(byte))
    ascii_code = ascii_code.replace('0b', '0', 1)
    b_data += ascii_code
  
  # print len(b_data)
  print b_data
  a.write(0, b_data)
  r_data = a.read(0, 2)
  print int(r_data) ^ int(b_data)