import socket
import sys
from chatuicurses import init_windows, read_command, print_message, end_windows

def runner_1():
    '''
    Listens for incoming messages
    '''
    ...

def runner_2():
    ...

def usage():
    print("usage: select_client.py prefix host port", file=sys.stderr)

def main(argv):

    try:
        prefix = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1
    
    init_windows()

    s = socket.socket()
    s.connect((host, port))

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
