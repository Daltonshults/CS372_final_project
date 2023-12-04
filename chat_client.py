import socket
import sys
import json
from chatuicurses import init_windows, read_command, print_message, end_windows

def runner_1():
    '''
    Listens for incoming messages
    '''
    ...

def runner_2():
    ...

def usage():
    print("usage: select_client.py name host port", file=sys.stderr)

def main(argv):

    try:
        name = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1
    
    init_windows()

    s = socket.socket()
    s.connect((host, port))

    # Create connection JSON and send it
    hello = {
        "type": "hello",
        "nick": name
    }

    hello_str = json.dumps(hello)
    hello_str_bytes = hello_str.encode()
    s.send(hello_str_bytes)


    while True:
        try:
            command = read_command("Enter a thing> ")
            command_bytes = command.encode()
            s.send(command_bytes)
        except:
            break

        print_message(f">>> {command}")
    
    end_windows()

if __name__ == "__main__":
    main(sys.argv)
