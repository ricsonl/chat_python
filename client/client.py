import socket
import threading

class Client:
  def __init__(self):
    while True:
      self.username = input('Nome de usuário: ') # nome do usuario
      if self.username: break #verifica se é diferente de ''
    
    self.online = False

    self.cmd = {# dicionario para os possíveis comandos do usuario
      'listusers': '/list',
      'sendfile': '/file',
      'getfile': '/get',
      'quit': '/bye',
    }

  def listen_server(self):#thread que ficara escutando novas mensagens vindas do servidor
    while self.online:
      sv_msg, serv = self.udp_socket.recvfrom(1024)
      wds = sv_msg.decode().split(':')
      if wds[0] == 'MSG':
        print(f'{wds[1]} disse: {wds[2]}')
      elif wds[0] == 'INFO':
        print(wds[1])

  def enter_chat(self, host, port):
    self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)# criacao do socket p/ troca de mensagens
    self.online = True
    self.dest = (host, port)# seta ip e porta de destino
    msg = f'USER:{self.username}'.encode()
    self.udp_socket.sendto(msg, self.dest) # envia mensagem de controle USER com seu username

    t = threading.Thread(target=self.listen_server)
    t.start()# inicia a thread que escuta o servidor

    while True:
      msg = input()
      if msg: break
    command = msg.split()[0]# para verificar se foi solicitado algum dos comandos de self.cmd
    while command != self.cmd['quit']:# enquanto o usuario nao digita '/bye {...}'
     
      if command == self.cmd['sendfile']:# caso o usuario tenha digitado '/file {...}'
        wds = msg.split()# separando o comando do nome do arquivo
        if len(wds) > 1:
          with open(wds[1], 'rb') as f:# abre o arquivo em binario
            self.send_file(wds[1], f)
            msg = f'FILE:{wds[1]}'.encode()# monta mensagem de controle
            self.udp_socket.sendto(msg, self.dest)# envia mensagem udp no formato FILE:<file>

      elif command == self.cmd['getfile']:# caso o usuario tenha digitado '/get {...}'
        wds = msg.split()# separando o comando do nome do arquivo
        if len(wds) > 1:
          msg = f'GET:{wds[1]}'.encode()# monta mensagem de controle
          self.udp_socket.sendto(msg, self.dest)# envia mensagem udp

      elif command == self.cmd['listusers']:# caso o usuario tenha digitado '/list {...}'
        msg = 'LIST'.encode()# monta mensagem de controle
        self.udp_socket.sendto(msg, self.dest)# envia para o servidor pelo socket udp
      
      elif msg[0] != '/':
        msg = f'MSG:{msg}'.encode()# monta mensagem de controle
        self.udp_socket.sendto(msg, self.dest)# envia para o servidor pelo socket udp

      while True:
        msg = input()
        if msg: break
      command = msg.split()[0]

    msg = 'BYE'.encode()
    self.udp_socket.sendto(msg, self.dest)# envia mensagem de controle (pelo socket udp) ao se desconectar
    self.online = False
    self.udp_socket.close()

  def send_file(self, filename, file):
    self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# criacao do socket p/ envio de arquivos
    self.tcp_socket.connect(self.dest)

    self.tcp_socket.send(f'{filename}\n'.encode())# pelo socket tcp, envia primeiramente o nome do arquivo seguido por \n
   
    l = file.read(1024)# le parte do arquivo
    while (l):# ate acabar o arquivo
      self.tcp_socket.send(l)# envia
      l = file.read(1024)# le outra parte do arquivo

    self.tcp_socket.close()

def main():
  host = '127.0.0.1'
  port = 2000
  c1 = Client()# inicia o cliente, configurando seu nome
  c1.enter_chat(host, port)
  
if __name__ == '__main__':
  main()