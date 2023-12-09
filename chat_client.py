import socket
import sys
import json
import threading
from chatuicurses import init_windows, read_command, print_message, end_windows

packet_buffer = b''
nick = ""

def select_response_type(json_packet):
    if json_packet["type"] == "chat" and json_packet["nick"] != nick:
                    print_message(f"{json_packet['nick']}: {json_packet['message']}")

    if json_packet["type"] == "join" and json_packet["nick"] != nick:
        print_message(f"*** {json_packet['nick']} has joined the chat")

    if json_packet["type"] == "leave" and json_packet["nick"] != nick:
        print_message(f"*** {json_packet['nick']} has left the chat")

def extract_packet_buffer(packet_buffer, packet_len):
     return packet_buffer[2:packet_len], packet_buffer[packet_len: ]

def get_json_packet(packet_data):

    json_str = packet_data.decode()
    return json.loads(json_str)

def data_empty(data):
     if len(data) == 0:
          return True

def runner_1(socket):
    '''
    Recieves packets from the server, and then displays those results
    on screen
    '''
    global packet_buffer
    global nick
    while True:
        if len(packet_buffer) > 2:

            packet_len = int.from_bytes(packet_buffer[:2], byteorder="big") + 2

            if packet_len <= len(packet_buffer):

                packet_data, packet_buffer = extract_packet_buffer(packet_buffer, packet_len)

                json_packet = get_json_packet(packet_data)

                select_response_type(json_packet)
        
        data = socket.recv(4096)

        if data_empty(data):
            print_message("No connection")
            break

        packet_buffer += data


def usage():
    print("usage: select_client.py name host port", file=sys.stderr)

def create_hello_string(name):
    
    hello = {
        "type": "hello",
        "nick": name
    }

    hello_str = json.dumps(hello)
    hello_str_bytes = hello_str.encode()
    
    return hello_str_bytes    

def create_message_string(command):
    '''
    ADD LENGTH TO THE PACKET
    '''
    message = {
        "type" : "chat",
        "message": command
    }

    message_str = json.dumps(message)

    return message_str.encode()

def create_message(msg):
    length = len(msg)
    bytes_lengths = length.to_bytes(2, byteorder="big")
    return bytes_lengths + msg

def check_for_quit(command):
     return command[0] == '/' and command[1] == 'q' and len(command) == 2

def main(argv):

    try:
        name = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1
    
    global nick 
    nick = name

    init_windows()

    s = socket.socket()
    s.connect((host, port))
    hello_msg = create_hello_string(name)

    s.send(create_message(hello_msg))

    t1 = threading.Thread(target=runner_1,
                          daemon=True,
                          args=(s,))
    t1.start()

    while True:
        try:
            command = read_command(f"{nick}> ")
            command_bytes = create_message_string(command)

            if check_for_quit(command):
                sys.exit(0)
            
            s.send(create_message(command_bytes))
        except:
            break

        print_message(f"{nick}: {command}")
    
    end_windows()

if __name__ == "__main__":
    main(sys.argv)
