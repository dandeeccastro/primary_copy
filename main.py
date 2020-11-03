import socket
import sys
import select
import re

def validateCommand(fullCommand):
    command = fullCommand.split()
    if command[0] == 'read':
        regex = re.compile('^read$')
    elif command[0] == 'history':
        regex = re.compile('^history$')
    elif command[0] == 'write':
        regex = re.compile('write [0-9]+')
    elif command[0] == 'close':
        regex = re.compile('^close$')
    else:
        return False
    match = regex.match(fullCommand)
    return bool(match)

def main(nodeID):
    print("[Node {0}] TODO implement me".format(nodeID))
    while True:
        inputs = [sys.stdin]
        r,w,x = select.select(inputs,[],[])

        for command in r:
            if command == sys.stdin:
                fullMessage = input()
                message = fullMessage.split()
                commandIsValid = validateCommand(fullMessage)

                if message[0] == 'read' and commandIsValid:
                    print("Ok {0}".format(message[0]))
                elif message[0] == 'history' and commandIsValid:
                    print("Ok {0}".format(message[0]))
                elif message[0] == 'write' and commandIsValid:
                    print("Ok {0}".format(message[0]))
                elif message[0] == 'close' and commandIsValid:
                    print("Ok {0}".format(message[0]))
                    sys.exit()

if __name__ == '__main__':
    nodeID = input('Insira o ID desse nó: ')
    main(nodeID)
