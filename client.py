import socket, os, time, json, re, pickle


##  CLIENT  ##

def ip_new():	
	while True:		
		error = False
		_ip = input("\n Enter ip: ")
		pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
		match = re.search(pattern, _ip)
		if match is not None:
			for i in match.groups():
				if (int(i) < 0 or int(i) > 255):
					error = True	
			if not error and check_conn(_ip):
				return _ip		


##  CONNECTIONS  ##

def check_conn(_ip):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
		try:
			client.connect( (_ip, port) )
			return True
		except Exception as e:
			print()
			print(e)
			return False
		

def user_send( _cmd, _data ):
	req_arr = [ _cmd, _data ]	
	request = pickle.dumps(req_arr)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
		client.connect( (server_ip, port) )
		#sv_resp = client.recv(64).decode('utf-8') # connection confirm

		client.send(request) 
		print('\n' + client.recv(256).decode('utf-8')) # server answer

		if _cmd == 'src':
			responce = client.recv(8128)
			if not responce:
				return None
			src_resp = pickle.loads(responce)
			return src_resp
	

##  RECORDS  ##

def record_show(_record):
	for val in _record:
		print(f"  {val:<15}: {_record[val]}")


def record_add():	
	print("\n -- Adding new record --")

	new_record = record_template
	for val in new_record:
		new_record[val] = input( str(val) + ": ")

	print()
	record_show(new_record)	
	user_send('add', new_record)

	match input("\n Press \"Enter\" to continue, or enter \"0\" to delete it: "):
		case '0': record_del(new_record)
		case _: return	


def record_search():
	print("\n -- Search for record -- \n")

	while True:
		for f in record_template:
			print(f"    {f}", end='')
		field = input("\n\n >> Enter field for search (from specified): ")
		if field in record_template:
			break;

	value = input(" >> Enter value for search: ")
	src_request = ( field, value )

	sv_resp = user_send( 'src', src_request )
	if sv_resp is not None and sv_resp != []:
		print("\n Record found:")
		count = 1
		for val in sv_resp:	
			print(f"\n {count}:")
			record_show(val)	
			count += 1		

		inp = input("\n Press \"Enter\" to continue, or enter number of record to delete it: ")			
		if inp == '':
			return
		elif inp.isdigit():
			if int(inp) < 1 or int(inp) > count:
				return
			else:
				record_del(sv_resp[int(inp) - 1])
	else:
		print("\n Record not found")


def record_del(_record):
	user_send('del', _record)


#===============================================================
#===============================================================


record_template = {
	'name':       '',
	'surname':    '',
	'patronymic': '',
	'phone':      '',
	'comment':    '',
}

server_ip = "127.0.0.1" # default
port = 2256
cmds = [ 'add', 'src' ] # available user commands 



print("\n == Phone book database client == ")
server_ip = ip_new()
cl_running = True

while cl_running:
	print("\n  add    -  Add new record.")
	print(  "  src    -  Search record by any field, then show it, delete it.\n")

	user_cmd = input(" Enter command: ")
	if user_cmd not in cmds:
		continue

	match user_cmd:
		case 'add':
			record_add()
		case 'src':
			record_search()

