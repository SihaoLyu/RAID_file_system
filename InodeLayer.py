'''
THIS MODULE IS INODE LAYER OF THE FILE SYSTEM. IT INCLUDES THE INODE DEFINITION DECLARATION AND GLOBAL HANDLE OF BLOCK LAYER OF API.
THIS MODULE IS RESPONSIBLE FOR PROVIDING ACTUAL BLOCK NUMBERS SAVED IN INODE ARRAY OF BLOCK NUMBERS TO FETCH DATA FROM BLOCK LAYER.
'''
import datetime, config, BlockLayer, InodeOps

#HANDLE OF BLOCK LAYER
interface = BlockLayer.BlockLayer()

class InodeLayer():

    #RETURNS BLOCK NUMBER FROM RESPECTIVE INODE DIRECTORY
    def INDEX_TO_BLOCK_NUMBER(self, inode, index):
        if index == len(inode.blk_numbers): return -1
        return inode.blk_numbers[index]


    #RETURNS BLOCK DATA FROM INODE
    def INODE_TO_BLOCK(self, inode, offset):
        index = offset / config.BLOCK_SIZE
        block_number = self.INDEX_TO_BLOCK_NUMBER(inode, index)
        if block_number == -1: return ''
        else: return interface.BLOCK_NUMBER_TO_DATA_BLOCK(block_number)


    #MAKES NEW INODE OBJECT
    def new_inode(self, type):
        return InodeOps.Table_Inode(type)


    #FLUSHES ALL THE BLOCKS OF INODES FROM GIVEN INDEX OF MAPPING ARRAY  
    def free_data_block(self, inode, index):
        for i in range(index, len(inode.blk_numbers)):
            interface.free_data_block(inode.blk_numbers[i])
            inode.blk_numbers[i] = -1


    #IMPLEMENTS WRITE FUNCTIONALITY
    def write(self, inode, offset, data):
        inode.time_accessed = str(datetime.datetime.now())[:19]
        if inode.type == 1:
            print('Can not write data to a directory!')
            return -1
        
        max_file_size = (config.INODE_SIZE - 63 - config.MAX_FILE_NAME_SIZE) / 2 * config.BLOCK_SIZE 
        if offset > max_file_size or offset < 0:
            print('Write position error!')
            return -1
        
        blk_index_offset = offset / config.BLOCK_SIZE
        byte_offset = offset % config.BLOCK_SIZE
        data_offset = 0
        length = len(data)
        if offset + length > max_file_size: 
            length = max_file_size - offset
            data = data[:length]
        blk_index_end = (offset + length) / config.BLOCK_SIZE
        if (offset + length) % config.BLOCK_SIZE != 0: blk_index_end += 1

        for index in range(blk_index_offset, blk_index_end):
            blk = inode.blk_numbers[index]
            blk_data = ''
            if blk == -1:
                blk = interface.get_valid_data_block()
                empty_data = '\0' * config.BLOCK_SIZE
                interface.update_data_block(blk, empty_data)
                inode.blk_numbers[index] = blk
                inode.size += config.BLOCK_SIZE
            if index == blk_index_offset:
                data_offset = config.BLOCK_SIZE - byte_offset
                blk_data += interface.BLOCK_NUMBER_TO_DATA_BLOCK(blk)[: byte_offset]
                blk_data += data[: data_offset]
            else:
                blk_data += data[data_offset : data_offset + config.BLOCK_SIZE]
                blk_data += interface.BLOCK_NUMBER_TO_DATA_BLOCK(blk)[len(blk_data):]    # if data.size < blk_size
                data_offset += config.BLOCK_SIZE
            
            interface.update_data_block(blk, blk_data)
        
        inode.time_modified = str(datetime.datetime.now())[:19]
        return inode

    #IMPLEMENTS THE READ FUNCTION 
    def read(self, inode, offset, length): 
        inode.time_accessed = str(datetime.datetime.now())[:19]
        if inode.type == 1:
            print('Can not read data to a directory!')
            return -1
        
        if offset > inode.size or offset < 0:
            print('Read position error!')
            return -1
        
        blk_index_offset = offset / config.BLOCK_SIZE
        byte_offset = offset % config.BLOCK_SIZE
        if offset + length > inode.size:   length = inode.size - offset
        blk_index_end = (offset + length) / config.BLOCK_SIZE
        if (offset + length) % config.BLOCK_SIZE != 0: blk_index_end += 1
        blk_data = ''
        data = ''
        for index in range(blk_index_offset, blk_index_end):    
            blk_data += interface.BLOCK_NUMBER_TO_DATA_BLOCK(inode.blk_numbers[index])

        data += blk_data[byte_offset : byte_offset+length]
        return [data, inode]

