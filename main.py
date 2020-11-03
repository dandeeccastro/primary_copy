import socket
import sys
import select

def main(nodeID):
    print("[Node {0}] TODO implement me".format(nodeID))
    while True:
        inputs = [sys.stdin]
        r,w,x = select.select(inputs,[],[])
        for command in r:
            if command == sys.stdin:
                fullMessage = input()
                message = fullMessage.split()
                if message[0] == 'read':
                    print("Ok {0}".format(message[0]))
                elif message[0] == 'history':
                    print("Ok {0}".format(message[0]))
                elif message[0] == 'write':
                    print("Ok {0}".format(message[0]))
                elif message[0] == 'close':
                    print("Ok {0}".format(message[0]))
                    sys.exit()

if __name__ == '__main__':
    nodeID = input('Insira o ID desse nó: ')
    main(nodeID)
