import socket, select
import time
from threading import Thread
import random

#HEADER
print("===================================================================================================================================")
print("Inicio da execuçao: Servidor que recebe requisiçoes de clientes e envia quantos crimes ocorreram em alguns países num período de tempo\n via streaming dados por UDP para os clientes")
print("Restriçoes: -Deve ser executado com python3\n            -O intervalo entre os envios de pacotes deve ser entre 1 e 1500 milissegundos")
print("            -É necessário usar o comando 'ctrl-Z' no terminal para encerrar o programa")
print("Alunos: Matheus Yukio Lopes Shimazu - GRR20171625\n        Roberta Samistraro Tomigian - GRR20171631")
print("Professor: Elias    -    Disciplina: Redes de Computadores II")
print("Data da ultima atualizacao: 07/06/19")
print("===================================================================================================================================")

localPort   = int(input("Porta usada pelo servidor: "))
intervalo = int(input ("Insira o intervalo entre o envio de pacotes em milissegundos: "))
while (intervalo>1500 or intervalo<1):
    intervalo = int(input ("Intervalo em milissegundos deve ser entre 1 e 1500 milissegundos: "))
intervalo = intervalo*0.001
#===============================================VARIAVEIS GLOBAIS===============================================
hostName = socket.gethostname() 
print("O nome do host local é: {}".format(hostName))

localIP     = socket.gethostbyname(hostName)
print("Endereço IP do host local é: {}".format(localIP))

bufferSize  = 1024

# Lista de clientes inscritos no streamming
CONNECTION_LIST = []

# Cria o socket UDP do servidor
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind ao endereço e IP
UDPServerSocket.bind((localIP, localPort))

# Aleatoriza os dados da lista de países
def rand_country(paises):
    length = len(paises)
    for i in range(length):
        paises[i] = random.randint(0,200)

# Converte a lista de paises e numero do pacote em string, para envio
def concatenates(number,paises):
    string = []
    number = str(number)
    string.append(number)
    string.append("/")
    length = len(paises)
    for i in range(length):
        paises[i] = str(paises[i])
        string.append(paises[i])
        string.append("/")
    string.pop(len(string)-1)
    string = ''.join(string)
    return string

print("Servidor UDP ligado e pronto para conexão")
#print("UDP server up and listening")

# Thread que recebe mensagem dos clientes e dependendo da mensagem adiciona ou remove da lista
def listenclient(threadname):
    # Listen for incoming datagrams
    global CONNECTION_LIST
    while(True):
        print(CONNECTION_LIST)
        print("")
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message, address = bytesAddressPair
        ip, port = address
        print("Cliente %s na porta %s enviou a mensagem: %s" %(ip, port, message.decode() ))
        if message.decode() != "Request":
        	CONNECTION_LIST.remove(address)
        	print("Cliente %s na porta %s foi removido da lista" %(ip, port))
        else:
        	CONNECTION_LIST.append(address)
        	print("Cliente %s na porta %s foi adicionado à lista" %(ip, port))

# Thread que gera os dados e envia para a lista de clientes
def sendtoclient(threadname):
    global CONNECTION_LIST
    global intervalo
    number = 1
    while (True):
        time.sleep(intervalo)
        paises = [0, 0, 0, 0, 0, 0]
        rand_country(paises)
        datatosend = concatenates(number,paises)
        for i in CONNECTION_LIST:                   
            # Envia dados para os clientes
            UDPServerSocket.sendto(datatosend.encode('utf-8'), i)
        number = number + 1 
        # teste para ver se encontra pacotes em ordem errada
        # if (number % 5) == 0:
            # number += 1
        # OBS: so pode rodar se tiver elemento na lista
#===============================================THREADS===============================================
listenclient = Thread( target=listenclient, args=("Thread-1", ) )
sendtoclient = Thread( target=sendtoclient, args=("Thread-2", ) )

listenclient.start()
sendtoclient.start()

listenclient.join()
sendtoclient.join()
