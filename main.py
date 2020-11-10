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
    elif command[0] == 'permission':
        regex = re.compile('^permission$')
    elif command[0] == 'help':
        regex = re.compile('^help$')
    else:
        return False
    match = regex.match(fullCommand)
    return bool(match)

def main(nodeID,items):
    # Inicializando X, histórico e permissão de escrita (chapéu)
    X = 0
    history = []
    hasWritePermission = len(items) == 0 # se é o primeiro, items é vazio e ele tem permissão de arquivo

    if len(items) > 0:
        for i in range(4201,4205):
            if i != 4200 + int(nodeID):
                sock = socket.socket()
                if sock.connect_ex(("localhost",i)) == 0:
                    sock.sendall(b"UPDATE")
                    data = sock.recv(1024).decode('utf-8')
        data = data.split()
        if len(data) > 1:
            X = int(data[0])
            history = formatHistoryData(data[1])
    
    del items

    # Prepara o soquete que espera conexões 
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind( ("localhost", 4200 + int(nodeID)) )
    listener.listen(1)

    while True:
        # Constantemente atualiza os inputs para ficar ouvindo 
        inputs = [sys.stdin, listener]
        r,w,x = select.select(inputs,[],[])

        for command in r:

            if command == sys.stdin:
                fullMessage = input()
                message = fullMessage.split()
                commandIsValid = validateCommand(fullMessage)

                # Leitura imprime o valor local de X na tela
                if message[0] == 'read' and commandIsValid:
                    print("[Node {0}] X = {1}".format(nodeID,X))

                # History imprime as mudanças registradas localmente 
                elif message[0] == 'history' and commandIsValid:
                    response = "[Node {0}]\n".format(nodeID)
                    if history:
                        for entry in history:
                            response += "Node {0} escreveu {1} \n".format(entry[0],entry[1])
                    else:
                        response += " X não foi alterado ainda"
                    print(response)

                # Write funciona diferentemente se ele tem o chapéu ou não 
                elif message[0] == 'write' and commandIsValid:
                    
                    responses = [] 
                    # Se ele não tem permissão, ele pede permissão e anota as respostas que recebe
                    if not hasWritePermission:
                        for i in range(4201,4205):
                            if i != 4200 + int(nodeID):
                                sock = socket.socket()
                                if sock.connect_ex(("localhost",i)) == 0:
                                    sock.sendall('TRANSFER'.encode('utf-8'))
                                    responses.append(sock.recv(1024).decode('utf-8'))

                    # Se uma das respostas for OK (que só o dono do chapéu permite), ele procede a mudar o valor e atualizar suas mudanças
                    if "OK" in responses or not len(responses):
                        hasWritePermission = True
                        X = int(message[1])
                        update = (nodeID,int(message[1]))
                        history.append(update)
                        for i in range(4201,4205):
                            if i != 4200 + int(nodeID):
                                sock = socket.socket()
                                if sock.connect_ex(("localhost",i)) == 0:
                                    sock.sendall('WRITE {0} {1}'.format( message[1], stringifyHistory(history) ).encode('utf-8'))

                # Close termina a execução do nó, e se o nó tem permissão de escrita, ele elege um novo por meio
                # do nó com maior ID na rede
                elif message[0] == 'close' and commandIsValid:
                    if hasWritePermission:
                        i = 4204
                        while i != 4200:
                            if i != 4200 + int(nodeID):
                                sock = socket.socket()
                                if sock.connect_ex(("localhost", i)) == 0:
                                    sock.sendall(b'ELECTED') 
                                    break
                            i -= 1
                    sys.exit()

                elif message[0] == 'permission' and commandIsValid:
                    print("[Node {}] Permissão de escrita: {}".format(nodeID,hasWritePermission))

                elif message[0] == 'help': 
                    if len(message) > 1:
                        if message[1] == 'read':
                            print("read: Lê o valor de X armazenado no nó em questão")
                        elif message[1] == 'write':
                            print("write <valor>: Escreve o valor em X (precisa ser um número inteiro)")
                        elif message[1] == 'history':
                            print("history: Imprime na tela o histórico de mudanças no valor de X, assim como qual nó mudou ele")
                        elif message[1] == 'close':
                            print("close: Fecha o sistema, atualizando os outros nós caso ele seja o dono da permissão de escrita ")
                        elif message[1] == 'permission':
                            print("permission: Imprime na tela se você tem permissão de escrita no momento. Comando para motivos de debugging")
                    else:
                        print("Comandos disponíveis: read, write, history, permission, close")

            # Caso o nó receba uma mensagem 
            elif command == listener:
                new_sock, addr = listener.accept()
                fullMsg = new_sock.recv(1024).decode('utf-8')
                msg = fullMsg.split()

                if not msg:
                    continue

                # Se o protocolo de escrita é recebido 
                if msg[0] == 'WRITE':

                    # O nó atualiza seu X e atualiza a história fazendo uma análise de que parte da história é repetida,
                    # para poder adicionar só o que é novo
                    X = int(msg[1])
                    stringifiedHistory = stringifyHistory( history )
                    print("[Node {0}] {1}".format( nodeID, stringifiedHistory in msg[2] ) )
                    cuttingIndex = msg[2].find(stringifiedHistory)
                    appendable = msg[2][cuttingIndex + len(stringifiedHistory):-1]
                    historyUpdate = formatHistoryData(appendable)
                    for newEntry in historyUpdate:
                        history.append(newEntry)

                # Se o protocolo de transferência de chapéu é chamado, ele manda INVALID se não for o dono
                # mas se for o dono, ele tira seu chapéu e dá OK para o nó botar o dele
                elif msg[0] == 'TRANSFER':
                    if hasWritePermission:
                        hasWritePermission = False
                        new_sock.sendall(b"OK")
                    else:
                        new_sock.sendall(b"INVALID")

                elif msg[0] == 'ELECTED':
                    hasWritePermission = True
                    print("[Node {}] Eleito para ser novo dono do chapéu, antigo dono desconectou".format(nodeID))

                elif msg[0] == 'UPDATE':
                    new_sock.sendall("{} {}".format(X,stringifyHistory(history)).encode('utf-8'))

if __name__ == '__main__':
    occupied = []
    for port in range (4201,4205):
        test_sock = socket.socket()
        if test_sock.connect_ex(("localhost",port)) == 0:
            occupied.append(port - 4200)
        test_sock.close()
    nodeID = int(input('Insira o ID desse nó (1-4): '))
    while nodeID in occupied:
        nodeID = int(input('Insira o ID desse nó (1-4): '))
    main(nodeID,occupied)
