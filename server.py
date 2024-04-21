import socket, os, time, json, re, pickle, threading


##  SERVER  ##

def is_ip(_ip):
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    match = re.search(pattern, _ip)
    if match is not None:
        for i in match.groups():
            if( int(i) < 0 or int(i) > 255 ):
                return False            
            return True
    return False


def enter_new_ip():
    while True:
        ip = input("Enter new ip: ")
        if is_ip( ip ):
            with open(server_cfg_file, 'w+') as file:                
                file.write(ip)
                return ip
        else:
            continue    


##  DATABASE  ##

def db_add(_data):
    with open(server_db_file, 'r', encoding='utf-8') as db:
        data = json.load(db)
        data['numbers'].append(_data)
        with open(server_db_file, 'w', encoding='utf-8') as db:
            json.dump(data, db, indent=2)


def db_del(_to_del):
    #time.sleep(10)
    with open(server_db_file, 'r', encoding='utf-8') as db:
        data = json.load(db)
        data['numbers'].remove(_to_del)
        with open(server_db_file, 'w', encoding='utf-8') as db:
           json.dump(data, db, indent=2)


def db_search( srcreq ):
    _field, _req = srcreq
    #time.sleep(15)
    with open(server_db_file, 'r', encoding='utf-8') as db:
        data = json.load(db)
        matches = []
        for val in data['numbers']:
            if val[_field] == _req:
                matches.append(val)
    return matches


##  CONNECTIONS  ##

def handle_conn( _conn, _conn_count ):    
    _user, _addr = _conn

    print(f"{_conn_count:0>6} Connection from {_addr}")
    connection = True

    while connection:
        request  = _user.recv(8128)        
        if not request:
            _user.send( "SERVER: Bad request".encode('utf-8') ) 
            break

        _user.send( "SERVER: Request accepted".encode('utf-8') )          
        req_arr = pickle.loads(request)
        cmd = req_arr[0]
        print(f"{_conn_count:0>6} Request from {_addr}: {req_arr}")

        match cmd:
            case 'add':
                db_add( req_arr[1] )

            case 'src':
                result = db_search( req_arr[1] )
                responce = pickle.dumps(result)
                _user.send(responce)

            case 'del': 
                db_del( req_arr[1] )

            case _: 
                _user.send( "SERVER: Bad request".encode('utf-8') )  

    print(f"{_conn_count:0>6} Drop from {_addr}")
        
    
#================================================================
#================================================================


server_ip = '127.0.0.1' # default
server_port = 2256      # const
server_db_file = "server_database.json"
server_cfg_file = "server_config.txt"


# checking cached ip
if os.path.exists( server_cfg_file ):
    with open(server_cfg_file, 'r') as file:
        ip = file.read()
        if is_ip(ip):
            while True:
                inp = input(f" Press \"Enter\" to use {ip} , or enter new ip: ")
                if inp == '':
                    server_ip = ip
                    break
                elif is_ip(inp):
                    server_ip = inp            
else:
    server_ip = enter_new_ip()

# database checking, creation
if not os.path.exists(server_db_file) or os.stat(server_db_file).st_size == 0:
    print("\n Data base file was created.")
    with open(server_db_file, 'w+', encoding='utf-8') as db:        
        data = { "numbers": [] }
        json.dump(data, db, indent = 4)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind( (server_ip, server_port) )
    server_socket.listen()
    server_run = True
    conn_count = 1
    
    print('\n -- server started --\n ip:   ' + str(server_ip) + '\n port: ' + str(server_port) + '\n')

    while server_run:
        try:
            connection = server_socket.accept()
            thread = threading.Thread( target=handle_conn, args=( connection, conn_count, ) )
            thread.start()   
            conn_count += 1
            
        except Exception as e:
            print("\n An error was occured!")
            print(e.strerror + "\n")
            server_run = False        

print("\n -- server stopped -- \n")


'''
data1 = {
    'name': 'Alex',
    'surname': 'asd',
    'patronymic': 'cfg',
    'phone': '89036456753', 
    'comment': 'comm'
}
'''
