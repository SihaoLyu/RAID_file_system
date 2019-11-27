import config, FileSystem, os, sys, Memory
interface = FileSystem.FileSystemOperations()
client = Memory.client
for i in range(int(sys.argv[1])):
		os.system('gnome-terminal -e \"python server_stub.py ' + str(8000+i) + '\"')

#GET SERVER PID
# pid_table = os.popen(r'ps a | grep "stub"').readlines()
# pid_num = []
# for entry in pid_table:
# 	if entry.find('server_stub.py') != -1: pid_num.append(entry)
# for index in range(len(pid_num)):	pid_num[index] = pid_num[index].split(" ")[0]

raid_mode = int(input('Please input raid mode (1 for RAID-1, 5 for RAID-5): '))
FileSystem.Initialize_My_FileSystem(int(sys.argv[1]), raid_mode)
while True:
	command_str = raw_input("$ ")
	raw_command_list = command_str.split(' ', 1)
	command = raw_command_list[0]
	if command == 'write':
		try:	
			data = command_str[command_str.index('"')+1 : command_str[command_str.index('"')+1:].index('"') + command_str.index('"')+1]
			command_str = command_str.replace('"'+ data +'"', "", 1)
			argv = command_str.split(" ")
			while bool(argv.count('')):
				argv.remove('')
			path = argv[1]
			offset = int(argv[2])
			interface.write(path, data, offset)
			continue
		except Exception as err:
			print('ERROR IN COMMAND INPUT, PLZ CHECK!')
	elif command == 'mkdir':
		try:	
			command_list = command_str.split(' ')
			path = command_list[1]
			interface.mkdir(path)
			continue
		except Exception as err:
			print('ERROR IN COMMAND INPUT, PLZ CHECK!')
	elif command == 'create':
		try:
			command_list = command_str.split(' ')
			path = command_list[1]
			interface.create(path)
			continue
		except Exception as err:
			print('ERROR IN COMMAND INPUT, PLZ CHECK!')
	elif command == 'mv':
		try:	
			command_list = command_str.split(' ')
			old_path = command_list[1]
			new_path = command_list[2]
			interface.mv(old_path, new_path)
			continue
		except Exception as err:
			print('ERROR IN COMMAND INPUT, PLZ CHECK!')
	elif command == 'rm':
		try:
			command_list = command_str.split(' ')
			path = command_list[1]
			interface.rm(path)
			continue
		except Exception as err:
			print('ERROR IN COMMAND INPUT, PLZ CHECK!')
	elif command == 'read':
		try:
			command_list = command_str.split(' ')
			path = command_list[1]
			offset = int(command_list[2])
			size = int(command_list[3])
			interface.read(path, offset, size)
			continue
		except Exception as err:
			print('ERROR IN COMMAND INPUT, PLZ CHECK!')
	elif command == 'status':
		try:
			interface.status()
			continue
		except Exception as err:
			print('ERROR IN COMMAND INPUT, PLZ CHECK!')
	elif command == 'exit':
		print('Filesystem exiting...')
		# for pid in pid_num: os.system('kill ' + str(pid))
		break
	elif command == "corruptdata":
		try:
			command_list = command_str.split(' ')
			server_id = int(command_list[1])
			client.CorruptData(server_id)
			continue
		except Exception as err:
			print('ERROR IN COMMAND INPUT, PLZ CHECK!')
	else:
		print('Wrong command input, please check!')
		continue


	

