import threading
import sys
from chatuicurses import init_windows, read_command, print_message, end_windows

def runner_1():
    ...

def runner_2():
    ...

def main(argv):
    init_windows()

    while True:
        try:
            command = read_command("Enter a thing> ")
        except:
            break

        print_message(f">>> {command}")

if __name__ == "__main__":
    main(sys.argv)
