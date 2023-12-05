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

# def print_socket_results(ready_to_be_read, list_s, read_set, buffers, names):
#     '''
#     Prints the results of the socket depending on the socket type.
#     The listening socket will add more connections to the read_set,
#     and non-listening sockets will print the messages that they
#     recieve.
#     '''
#     for s in ready_to_be_read:
        
#         # If the current connection is a listening socket
#         if s == list_s:
#             conn, addr = s.accept()
#             buffers[conn] = b''
#             read_set.add(conn)
#             host, port = conn.getpeername()

#             print("({}, {}): connected".format(host, port))
#             # SEND CONNECTION TO CLIENTS
                
#         else:

#             data = s.recv(4096)

#             # If the data is recieved without length the connection has been closed
#             if len(data) == 0:
#                 host, port = s.getpeername()
                    
#                 print("({}, {}): disconnected".format(host, port))
                
#                 # Remove closed connections from read_set
#                 read_set.remove(s)

#                 # SEND END OF CONNECTION TO CLIENTS
                    
#             else:
#                 # The message is from a non-closed connection. Print it. 
#                 host, port = s.getpeername()
#                 msg_len = len(data)
#                 print("({}, {}) {} bytes: {}".format(host, port, msg_len, data))
#                 for sock in read_set:

#                     if sock != list_s:

#                         length = len(data) + 2
#                         length_bytes = length.to_bytes(2, byteorder="big")
#                         packet_with_length = length_bytes + data
#                         sock.send(packet_with_length)


def while_select(read_set, list_s):
    '''
    Looping through and selecting connections that are ready,
    and passes them to the print socket results.
    '''
    names = dict()
    buffers = dict()
    packet_data = b''
    while True:
        ready_to_be_read, _, _ = select.select(read_set, {}, {})        
        
        for s in ready_to_be_read:
            
            # If the current connection is a listening socket
            if s == list_s:
                conn, addr = s.accept()
                buffers[conn] = b''
                read_set.add(conn)
                host, port = conn.getpeername()

                print("({}, {}): connected".format(host, port))
                # SEND CONNECTION TO CLIENTS
                    
            else:

                data = s.recv(4096)

                # If the data is recieved without length the connection has been closed
                if len(data) == 0:
                    host, port = s.getpeername()
                        
                    print("({}, {}): disconnected".format(host, port))
                    
                    # Remove closed connections from read_set
                    read_set.remove(s)

                    leave = {
                        "type": "leave",
                        "nick": names[s],
                    }

                    names.pop(s)

                    leave_str = json.dumps(leave)

                    leave_bytes = leave_str.encode()
                    length = len(leave_bytes)
                    leave_length_bytes = length.to_bytes(2, byteorder="big")
                    packet_with_length = leave_length_bytes + leave_bytes

                    sock.send(packet_with_length)

                    # SEND END OF CONNECTION TO CLIENTS
                buffers[s] += data

                print(f'length of buffer s {len(buffers[s])}')

                if (len(buffers[s]) > 2):
                    # The message is from a non-closed connection. Print it. 
                    host, port = s.getpeername()
                    msg_len = len(buffers[s])
                    print(f"BUFFERS {buffers[s]}")
                    
                    #print("({}, {}) {} bytes: {}".format(host, port, msg_len, data))

                    packet_len = int.from_bytes(buffers[s][:2], byteorder="big") + 2

                    print(f"packet len {packet_len}")
                    if packet_len <= len(buffers[s]):
                        packet_data = buffers[s][2:packet_len]
                        print("RESET BUFFER")
                        buffers[s]  =  b''

                        print("PACKET DATA :" + str(packet_data))
                    for sock in read_set:

                        if sock != list_s:
                            
                            length = len(packet_data)
                            length_bytes = length.to_bytes(2, byteorder="big")
                            packet_with_length = length_bytes + packet_data
                            json_str = json.loads(packet_data)

                            print(f"JSON STRING {json_str['type']}")
                            print(f"SEND THE STUPID FUCKING SHIT: {packet_with_length}")

                            if json_str['type'] == 'hello':
                                names[s] = json_str['nick']
                                join = {
                                    "type" : "join",
                                    "nick" : names[s],
                                 }
                                
                                join_str = json.dumps(join)
                                bytes_join = join_str.encode()
                                length = len(bytes_join)
                                print(f"LENGTH {length}")
                                length_bytes = length.to_bytes(2, byteorder="big")
                                packet_with_length = length_bytes +  bytes_join

                                sock.send(packet_with_length)

                            if json_str["type"] == "chat":
                                new_json = dict()
                                json_str["nick"] = names[s]
                                new_json['type'] = json_str['type']
                                new_json['nick'] = names[s]
                                new_json["message"] = json_str["message"]

                                strings_json = json.dumps(new_json)

                                print(f"STRINGS_JSON: {strings_json}")

                                print(f"NAME S: {names[s]}")
                                bytes_json = strings_json.encode()
                                length = len(strings_json)
                                length_bytes = length.to_bytes(2, byteorder="big")
                                packet_with_length = length_bytes + bytes_json


                                sock.send(packet_with_length)

                            # sock.send(packet_with_length)
                            # buffers[s] = b''

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