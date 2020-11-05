import socket
import sys
import select
import re

def formatHistoryData(historyData):
    print(historyData)

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
    X = 0
    history = []
    hasWritePermission = True
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind( ("localhost", 4200 + int(nodeID)) )
    listener.listen(1)

    while True:
        inputs = [sys.stdin, listener]
        r,w,x = select.select(inputs,[],[])

        for command in r:
            if command == sys.stdin:
                fullMessage = input()
                message = fullMessage.split()
                commandIsValid = validateCommand(fullMessage)

                if message[0] == 'read' and commandIsValid:
                    print("[Node {0}] X = {1}".format(nodeID,X))
                elif message[0] == 'history' and commandIsValid:
                    response = "[Node {0}]\n".format(nodeID)
                    if history:
                        for entry in history:
                            response += "Node {0} escreveu {1} \n".format(entry[0],entry[1])
                    else:
                        response += " X não foi alterado ainda"
                    print(response)
                elif message[0] == 'write' and commandIsValid:
                    if hasWritePermission:
                        X = int(message[1])
                        history.append((nodeID,int(message[1])))
                    print("[Node {0}] Escreveu {1} em X".format(nodeID,int(message[1])))
                elif message[0] == 'close' and commandIsValid:
                    print("Ok {0}".format(message[0]))
                    sys.exit()

            elif command == listener:
                new_sock, addr = listener.accept()
                fullMsg = new_sock.recv(1024).decode('utf-8')
                msg = fullMsg.split()

                if msg[0] == 'WRITE':
                    X = int(msg[1])
                    historyUpdate = formatHistoryData(msg[2])

if __name__ == '__main__':
    nodeID = input('Insira o ID desse nó: ')
    main(nodeID)
