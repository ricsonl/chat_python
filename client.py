import socket
import threading

class Client:
  def __init__(self):
    self.username = input('Nome de usuário: ') # nome do usuario
    self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)# criacao do socket p/ troca de mensagens
    self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# criacao do socket p/ envio de arquivos

    self.cmd = {# dicionario para os possíveis comandos do usuario
      'list': '/list',
      'file': '/file',
      'get': '/get',
      'quit': '/bye',
    }

  def listen_server(self):#thread que ficara escutando novas mensagens vindas do servidor
    while True:
      sv_msg, serv = self.udp_socket.recvfrom(1024)
      wds = sv_msg.decode().split(':')
      if wds[0] == 'MSG':
        print(f'{wds[1]} disse: {wds[2]}')
      elif wds[0] == 'INFO':
        print(wds[1])

  def enter_chat(self, host, port):
    self.dest = (host, port)# seta ip e porta de destino
    msg = f'USER:{self.username}'.encode()
    self.udp_socket.sendto(msg, self.dest) # envia mensagem de controle USER com seu username

    t = threading.Thread(target=self.listen_server)
    t.start()# inicia a thread que escuta o servidor

    msg = input()
    command = msg.split()[0]# para verificar se foi solicitado algum dos comandos de self.cmd
    while command != self.cmd['quit']:# enquanto o usuario nao digita '/bye {...}'
     
      if command == self.cmd['file']:# caso o usuario tenha digitado '/file {...}'
        wds = msg.split()# separando o comando do nome do arquivo
        if len(wds) > 1:
          msg = f'FILE:{wds[1]}'.encode()# converte para o padrao do protocolo utilizado
      elif command == self.cmd['get']:# caso o usuario tenha digitado '/get {...}'
        wds = msg.split()# separando o comando do nome do arquivo
        if len(wds) > 1:
          msg = f'GET:{wds[1]}'.encode()# converte para o padrao do protocolo utilizado
      elif command == self.cmd['list']:# caso o usuario tenha digitado '/list {...}'
        msg = 'LIST'.encode()# converte para o padrao do protocolo utilizado
        self.udp_socket.sendto(msg, self.dest)# envia para o servidor pelo socket udp
      
      elif msg != '':
        msg = f'MSG:{msg}'.encode()# converte para o padrao do protocolo utilizado
        self.udp_socket.sendto(msg, self.dest)# envia para o servidor pelo socket udp

      msg = input()
      command = msg.split()[0]

    msg = 'BYE'.encode()
    self.udp_socket.sendto(msg, self.dest)# envia mensagem de controle (pelo socket udp) ao se desconectar
    self.udp_socket.close()

def main():
  host = '127.0.0.1'
  port = 2000
  c1 = Client()# inicia o cliente, configurando seu nome
  c1.enter_chat(host, port)# conecta o
  
if __name__ == '__main__':
  main()