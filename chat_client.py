import socket
import sys
import json
import threading
from chatuicurses import init_windows, read_command, print_message, end_windows
packet_buffer = b''
nick = ""

def runner_1(socket):
    '''
    Recieves packets from the server, and then displays those results
    on screen
    '''
    global packet_buffer
    while True:
        print_message(str(packet_buffer))
        print_message("LENGTH BUFFER: " + str(len(packet_buffer)))
        if len(packet_buffer) > 2:

            packet_len = int.from_bytes(packet_buffer[:2], byteorder="big") + 2
            print_message("This is the packet length " + str(packet_len))
            if packet_len <= len(packet_buffer):

                packet_data = packet_buffer[2:packet_len]
                packet_buffer = packet_buffer[packet_len: ]


                json_str = packet_data.decode()
                print_message("THIS IS THE JSON: " + json_str)
                print_message("THIS IS THE PACKET DATA " + str(packet_data))
                json_packet = json.loads(json_str)

                print_message("JSON PACKET: " + str(json_packet))
                print_message(json_packet["type"])
        
        data = socket.recv(4096)

        if len(data) == 0:
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


def main(argv):

    try:
        name = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1
    
    nick = name

    init_windows()

    s = socket.socket()
    s.connect((host, port))
    hello = create_hello_string(name)

    length_hello = len(hello)
    length_bytes = length_hello.to_bytes(2, byteorder="big")
    hello_with_length = length_bytes + hello
    s.send(hello_with_length)

    t1 = threading.Thread(target=runner_1,
                          daemon=True,
                          args=(s,))
    t1.start()

    while True:
        try:
            command = read_command("Enter a thing> ")
            command_bytes = create_message_string(command)
            command_len = len(command_bytes)
            byte_len = command_len.to_bytes(2, byteorder="big")
            command_with_length = byte_len + command_bytes
            s.send(command_with_length)
        except:
            break

        print_message(f">>> {command}")
    
    end_windows()

if __name__ == "__main__":
    main(sys.argv)
