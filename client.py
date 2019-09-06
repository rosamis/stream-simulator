import socket
from threading import Thread
import sys
import os
import time

#HEADER
print("===================================================================================================================================")
print("Inicio da execuçao: Cliente envia requisição para o servidor, que mandará dados sobre crimes em diversos países via streaming por UDP")
print("Restriçoes: -Deve ser executado com python3\n            -Deve ser executado depois do servidor")
print("Alunos: Matheus Yukio Lopes Shimazu - GRR20171625\n        Roberta Samistraro Tomigian - GRR20171631")
print("Professor: Elias    -    Disciplina: Redes de Computadores II")
print("Data da ultima atualizaçao: 07/06/19")
print("===================================================================================================================================")
server=input("Digite o nome da máquina do servidor: ")
port=int(input("Digite o número da porta usada pelo servidor: "))

print("\n\nEscolha um dentre os seguintes países para descobrir a quantidade de crimes:")
print("   0 - Brasil\n   1 - Estados Unidos da América\n   2 - Canadá\n   3 - Arábia Saudita\n   4 - África do Sul\n   5 - Japão")
country = int(input ("Selecione o país por seu respectivo número: "))
while ((country>5) or (country<0)):
	country = int(input ("Número inválido, tente novamente: "))

#===============================================VARIAVEIS GLOBAIS===============================================
stat = 1
all_packets = 0
received_packets = 0
late_packets = 0
wrong_packets = 0
current_packet = 0
hits = 0
bufferSize = 1024
# List of previous packets for debugging
LIST_N = [] 

#Envia mensagem para o servidor afim de se inscrever na lista
msgFromClient       = "Request"
bytesToSend         = str.encode(msgFromClient)
hostName = socket.gethostname() 
serverAddressPort = (socket.gethostbyname(server), port)

# Cria socket do cliente
UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Envia para o servidor
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

#Dicionário para achar o nome baseado no número
def nome_pais(x):
	return {
		0:"Brasil",
		1:"EUA",
		2:"Canadá",
		3:"Arábia Saudita",
		4:"África do Sul",
		5:"Japão"
	}[x]

#Converte a string recebida pelo servidor em uma lista, para acessar os dados do pais escolhido e verifica a corretude do número do pacote
def process(string,country):
	global hits
	global wrong_packets
	global current_packet
	global received_packets

	os.system("clear")
	string = string.split('/')
	number = int(string[0])
	if received_packets == 1:
		current_packet = number
	elif number != (current_packet+1):
		wrong_packets += 1
		print("PACOTE ERRADO RECEBIDO")
	current_packet = number
	#print for debugging
	print(string)
	print("Número de ocorrências em %s no instante %s foi %s" %(nome_pais(country),(string[0]),string[country + 1]))
	hits += int(string[country+1])

#used for debugging
def separates(string):
    global LIST_N
    string = string.split('/')
    x = int(string[0])
    LIST_N.append(x)

##Thread que ouve o terminal e quando detecta um ENTER, envia uma mensagem para o servidor, para finalizar conexão
def sendto_server(threadname):
    global UDPClientSocket
    global serverAddressPort
    global stat

    x = input()
    UDPClientSocket.sendto(str.encode("Quit"), serverAddressPort)
    stat = 0
    print("Encerramento da conexão requisitado, aguarde ...")

#Thread que recebe dados do servidor e printa no terminal
def receivefrom_server(threadname):
    global bufferSize
    global UDPClientSocket
    #global LIST_N
    global stat
    global all_packets
    global received_packets
    global late_packets
    global country

    temp_timeout = 1.5
    while(True):
        #Seta o timeout
        UDPClientSocket.settimeout(temp_timeout)
        #Se os dados forem recebidos do servidor
        try:
            if stat == 0:
                break
            elif stat == 1:
                received_bytes, peer = UDPClientSocket.recvfrom(bufferSize)
                all_packets += 1
                received_packets += 1
                process(received_bytes.decode('utf8'),country)
                #3 next lines are for DEBUGGING
                #separates(received_bytes.decode('utf8'))
                #for elem in LIST_N:
                    #print ("Número do pacote: %s" %(LIST_N[elem]))
                print("\n")
        #Se os dados não forem recebidos pelo servidor, printa que expirou e marque os dados como atrasados
        except socket.timeout:
        	if stat == 0:
        		break
        	print ("REQUEST TIMED OUT")
        	all_packets += 1
        	late_packets += 1
            #aumenta o tempo do timeout para reduzir perda de pacotes
            #timeout = timeout + 0.25
            #descarta o pacote atrasado
        	received_bytes, peer = UDPClientSocket.recvfrom(bufferSize)
    #print("saiu do while")

#===============================================THREADS===============================================
sendto_server = Thread( target=sendto_server, args=("Thread-1", ))
receivefrom_server = Thread( target=receivefrom_server, args=("Thread-2", ))

sendto_server.start()
receivefrom_server.start()

sendto_server.join()
receivefrom_server.join()
#===============================================STATISTICS===============================================
print("Conexão encerrada com sucesso\n")
print("ESTATÍSTICAS:\n              Pacotes esperados       -> %s pacotes" %(all_packets))
print("              Pacotes recebidos       -> %s pacotes" %(received_packets))
print("              Pacotes atrasados       -> %s pacotes" %(late_packets))
print("              Pacotes em ordem errada -> %s pacotes" %(wrong_packets))
print("\nNúmero de ocorrências em %s desde o começo da execuçao do cliente: %s ocorrências." %(nome_pais(country),hits))

print("Programa encerrado com sucesso")
