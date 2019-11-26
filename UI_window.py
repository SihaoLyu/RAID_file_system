import config, FileSystem, os, sys, Memory
interface = FileSystem.FileSystemOperations()
client = Memory.client
for i in range(int(sys.argv[1])):
		os.system('gnome-terminal -e \"python server_stub.py ' + str(8000+i) + '\"')
FileSystem.Initialize_My_FileSystem(int(sys.argv[1]))
while True:
	command_str = raw_input("$ ")
	raw_command_list = command_str.split(' ', 1)
	command = raw_command_list[0]
	if command == 'write':
		data = command_str[command_str.index('"')+1 : command_str[command_str.index('"')+1:].index('"') + command_str.index('"')+1]
		command_str = command_str.replace('"'+ data +'"', "", 1)
		argv = command_str.split(" ")
		while bool(argv.count('')):
			argv.remove('')
		path = argv[1]
		offset = int(argv[2])
		interface.write(path, data, offset)
		continue
	elif command == 'mkdir':
		command_list = command_str.split(' ')
		path = command_list[1]
		interface.mkdir(path)
		continue
	elif command == 'create':
		command_list = command_str.split(' ')
		path = command_list[1]
		interface.create(path)
		continue
	elif command == 'mv':
		command_list = command_str.split(' ')
		old_path = command_list[1]
		new_path = command_list[2]
		interface.mv(old_path, new_path)
		continue
	elif command == 'rm':
		command_list = command_str.split(' ')
		path = command_list[1]
		interface.rm(path)
		continue
	elif command == 'read':
		command_list = command_str.split(' ')
		path = command_list[1]
		offset = int(command_list[2])
		size = int(command_list[3])
		interface.read(path, offset, size)
		continue
	elif command == 'status':
		interface.status()
		continue
	elif command == 'exit':
		print('Filesystem exiting...')
		break
	elif command == "corruptdata":
		server_id = int(command_list[1])
		client.CorruptData(server_id)
		continue
	else:
		print('Wrong command input, please check!')
		continue


	

