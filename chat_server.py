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

def check_msg_type(json_str, names, buffers, sock, s):
    if json_str['type'] == 'hello':
        names[s] = json_str['nick']
        join = {
            "type" : "join",
            "nick" : names[s],
            }
                                
        join_str = json.dumps(join)
        bytes_join = join_str.encode()
        length = len(bytes_join)

        length_bytes = length.to_bytes(2, byteorder="big")
        packet_with_length = length_bytes +  bytes_join

        sock.send(packet_with_length)
        buffers[s] = b''

    if json_str["type"] == "chat":
        new_json = dict()
        json_str["nick"] = names[s]
        new_json['type'] = json_str['type']
        new_json['nick'] = names[s]
        new_json["message"] = json_str["message"]

        strings_json = json.dumps(new_json)

        bytes_json = strings_json.encode()
        length = len(strings_json)
        length_bytes = length.to_bytes(2, byteorder="big")
        packet_with_length = length_bytes + bytes_json


        sock.send(packet_with_length)
        buffers[s] = b''


def initialize_names_buffers():
    return dict(), dict()

def add_to_read_set(s, buffers, read_set):
    conn, _ = s.accept()
    buffers[conn] = b''
    read_set.add(conn)

def data_empty(data):
    return len(data) == 0

def create_packet(msg):
    length = len(msg)
    length_bytes = length.to_bytes(2, byteorder="big")

    return length_bytes + msg

def send_packets(sock, read_set, list_s, packet_with_length):
    for sock in read_set:
        if sock != list_s:
            sock.send(packet_with_length)

def buffer_contain_length(buffer, packet_len):
    return packet_len <= len(buffer)

def while_select(read_set, list_s):
    '''
    Looping through and selecting connections that are ready,
    and passes them to the print socket results.
    '''
    names, buffers = initialize_names_buffers()
    packet_data = b''
    while True:
        ready_to_be_read, _, _ = select.select(read_set, {}, {})        
        
        for s in ready_to_be_read:
            
            # If the current connection is a listening socket
            if s == list_s:

                add_to_read_set(s,
                                buffers,
                                read_set)
                   
            else:

                data = s.recv(4096)

                # If the data is recieved without length the connection has been closed
                if data_empty(data):
                 
                    # Remove closed connections from read_set
                    read_set.remove(s)

                    leave = {
                        "type": "leave",
                        "nick": names[s],
                    }

                    names.pop(s)

                    leave_str = json.dumps(leave)

                    leave_bytes = leave_str.encode()

                    packet_with_length = create_packet(leave_bytes)

                    send_packets(sock,
                                 read_set,
                                 list_s,
                                 packet_with_length)


                buffers[s] += data


                if (len(buffers[s]) > 2):

                    packet_len = int.from_bytes(buffers[s][:2], byteorder="big") + 2


                    if buffer_contain_length(buffers[s], packet_len):
                        packet_data = buffers[s][2:packet_len]

                        buffers[s]  =  b''
                    for sock in read_set:

                        if sock != list_s:
                            packet_with_length = create_packet(packet_data)

                            json_str = json.loads(packet_data)

                            check_msg_type(json_str,
                                           names,
                                           buffers,
                                           sock,
                                           s)


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