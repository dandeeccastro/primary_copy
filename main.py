import socket
import sys
import select
import re

def formatHistoryData(historyData):
    if historyData:
        history = list(filter(lambda x: len(x),historyData.split(';')))
        result = []
        for entry in history:
            updatedEntry = entry.split(',')
            result.append( (updatedEntry[0], updatedEntry[1]) )
        return result
    else:
        return []

def stringifyHistory(history):
    result = ""
    if len(history):
        for entry in history:
            result += "{0},{1};".format(entry[0],entry[1])
    return result

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

def main(nodeID,items):
    X = 0
    history = []
    hasWritePermission = len(items) == 0
    del items
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
                    test = stringifyHistory(history)
                    print(test,formatHistoryData(test))
                elif message[0] == 'write' and commandIsValid:
                    if hasWritePermission:
                        X = int(message[1])
                        update = (nodeID,int(message[1]))
                        history.append(update)
                        for i in range(4201,4205):
                            if i != 4200 + int(nodeID):
                                sock = socket.socket()
                                if sock.connect_ex(("localhost",i)) == 0:
                                    sock.sendall('WRITE {0} {1}'.format( message[1], stringifyHistory(history) ).encode('utf-8'))
                    else:
                        responses = [] 
                        for i in range(4201,4205):
                            if i != 4200 + int(nodeID):
                                sock = socket.socket()
                                if sock.connect_ex(("localhost",i)) == 0:
                                    sock.sendall('TRANSFER'.encode('utf-8'))
                                    responses.append(sock.recv(1024).decode('utf-8'))
                        for response in responses:
                            if response == "OK":
                                hasWritePermission = True
                                X = int(message[1])
                                update = (nodeID,int(message[1]))
                                history.append(update)
                                for i in range(4201,4205):
                                    if i != 4200 + int(nodeID):
                                        sock = socket.socket()
                                        if sock.connect_ex(("localhost",i)) == 0:
                                            sock.sendall('WRITE {0} {1}'.format( message[1], stringifyHistory(history) ).encode('utf-8'))
                    print("[Node {0}] Escreveu {1} em X".format(nodeID,int(message[1])))
                elif message[0] == 'close' and commandIsValid:
                    print("Ok {0}".format(message[0]))
                    sys.exit()

            elif command == listener:
                new_sock, addr = listener.accept()
                fullMsg = new_sock.recv(1024).decode('utf-8')
                msg = fullMsg.split()

                if not msg:
                    continue

                if msg[0] == 'WRITE':
                    X = int(msg[1])
                    stringifiedHistory = stringifyHistory( history )
                    print("[Node {0}] {1}".format( nodeID, stringifiedHistory in msg[2] ) )
                    cuttingIndex = msg[2].find(stringifiedHistory)
                    appendable = msg[2][cuttingIndex + len(stringifiedHistory):-1]
                    historyUpdate = formatHistoryData(appendable)
                    for newEntry in historyUpdate:
                        history.append(newEntry)

                elif msg[0] == 'TRANSFER':
                    if hasWritePermission:
                        hasWritePermission = False
                        new_sock.sendall(b"OK")
                    else:
                        new_sock.sendall(b"INVALID")


if __name__ == '__main__':
    occupied = []
    for port in range (4201,4205):
        test_sock = socket.socket()
        if test_sock.connect_ex(("localhost",port)) == 0:
            occupied.append(port - 4200)
        test_sock.close()
    print(occupied)
    nodeID = int(input('Insira o ID desse nó (1-4): '))
    while nodeID in occupied:
        nodeID = int(input('Insira o ID desse nó (1-4): '))
    main(nodeID,occupied)
