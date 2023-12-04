import sys
import socket
import select
import json

def setup_socket(port):
    '''
    Returns a listening socket that has been set to the current
    port
    '''
    list_s = socket.socket()
    list_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    list_s.bind(('', int(port)))
    
    list_s.listen()

    return list_s

def create_read_set(list_s):
    '''
    Creates a set and adds a listening socket that is passed in 
    to that set, and returns the read_set
    '''
    read_set = set()
    read_set.add(list_s)

    return read_set

def print_socket_results(ready_to_be_read, list_s, read_set):
    '''
    Prints the results of the socket depending on the socket type.
    The listening socket will add more connections to the read_set,
    and non-listening sockets will print the messages that they
    recieve.
    '''
    for s in ready_to_be_read:
        
        # If the current connection is a listening socket
        if s == list_s:
            conn, addr = s.accept()
                
            read_set.add(conn)
            host, port = conn.getpeername()

            print("({}, {}): connected".format(host, port))
                
        else:

            data = s.recv(4096)

            # If the data is recieved without length the connection has been closed
            if len(data) == 0:
                host, port = s.getpeername()
                    
                print("({}, {}): disconnected".format(host, port))
                
                # Remove closed connections from read_set
                read_set.remove(s)
                    
            else:
                # The message is from a non-closed connection. Print it. 
                host, port = s.getpeername()
                msg_len = len(data)
                print("({}, {}) {} bytes: {}".format(host, port, msg_len, data))

def while_select(read_set, list_s):
    '''
    Looping through and selecting connections that are ready,
    and passes them to the print socket results.
    '''
    while True:
        ready_to_be_read, _, _ = select.select(read_set, {}, {})        
        
        print_socket_results(ready_to_be_read, list_s, read_set)

def run_server(port):

    list_s = setup_socket(port)

    read_set = create_read_set(list_s)

    while_select(read_set, list_s)


#--------------------------------#
# Do not modify below this line! #
#--------------------------------#

def usage():
    print("usage: chat_server.py port", file=sys.stderr)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))