import config, FileSystem, client_stub, sys
interface = FileSystem.FileSystemOperations()
FileSystem.Initialize_My_FileSystem(sys.argv[0])
while True:
	command_str = raw_input("$ ")
	command_list = command_str.split(' ')
	if len(command_list) == 2:
		command = command_list[0]
		path = command_list[1]
		if command == 'mkdir':
			interface.mkdir(path)
			continue
		elif command == 'create':
			interface.create(path)
			continue
		elif command == 'rm':
			interface.rm(path)
			continue
		else:
			print('Wrong command input, please check!')
			continue
	elif len(command_list) == 3:
		command = command_list[0]
		old_path = command_list[1]
		new_path = command_list[2]
		if command == "mv":
			interface.mv(old_path, new_path)
			continue
		else:
			print('Wrong command input, please check!')
			continue
	elif len(command_list) == 4:
		command = command_list[0]
		path = command_list[1]
		if command == 'read':
			offset = command_list[2]
			size = command_list[3]
			interface.read(path, offset, size)
			continue
		elif command == 'write':
			data = command_list[2]
			offset = command_list[3]
			interface.write(path, data, offset)
			continue
		else:
			print('Wrong command input, please check!')
			continue
	elif len(command_list) == 1:
		command = command_list[0]
		if command == 'exit':
			print('Exit command received.')
			break
		else:
			print('Wrong command input, please check!')
			continue
	else:
		print('Wrong command input, plz check!')
		continue

