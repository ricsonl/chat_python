import socket
import threading

class Server:
  def __init__(self, host, port):
    self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)# configuracao do socket p/ troca de mensagens
    self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# configuracao do socket p/ recebimento de arquivos
    self.orig = (host, port)
    self.clients = {}

  def start(self):
    self.udp_socket.bind(self.orig)
    #self.tcp_socket.bind(self.orig)
    #self.tcp_socket.listen(1)
    print('Aguardando conexão')
    while True:
      msg, client_udp = self.udp_socket.recvfrom(1024)# recebe mensagens pelo socket udp
      self.client_msg_dec(msg, client_udp)
      #con, client_tcp = self.tcp_socket.accept()# inicia o socket tcp para recebimento de arquivos
      #t = threading.Thread(target=tcp_conectado, args=(con, client_tcp))
      #t.start()

      
    self.udp_socket.close()
  
  def tcp_conectado(self, con, client):
    while True:
      msg = con.recv(1024).decode()
      #TODO ESTABELECER CONEXAO PARA TRANSFERENCIA DO ARQUIVO

  def client_msg_dec(self, msg, client_udp):# "decodifica" a mensagem recebida pelo cliente e faz os procedimentos requeridos
    wds = msg.decode().split(':')
    if wds[0] == 'USER':
      fmt = f'INFO:{wds[1]} entrou'# mensagem formatada para envio
      print(fmt)
      for c in self.clients.keys():# para cada cliente
        self.udp_socket.sendto(fmt.encode(), c)# envia mensagem de controle informando que o cliente entrou
      self.clients[client_udp] = wds[1]# armazena o nome de usuario na posicao (ip,port)
    elif wds[0] == 'MSG':
      fmt = f'MSG:{self.clients[client_udp]}:{wds[1]}'# mensagem formatada para envio
      print(fmt)
      for c in self.clients.keys():# para cada cliente
        if c != client_udp:# se nao for o proprio cliente que enviou a mensagem
          self.udp_socket.sendto(fmt.encode(), c)# envia a mensagem para todos
    elif wds[0] == 'FILE':
      pass
    elif wds[0] == 'GET':
      pass
    elif wds[0] == 'BYE':
      fmt = f'INFO:{self.clients[client_udp]} saiu'# mensagem formatada para envio
      print(fmt)
      self.clients.pop(client_udp)# remove o cliente do dicionario
      for c in self.clients.keys():# para cada cliente
        self.udp_socket.sendto(fmt.encode(), c)# envia mensagem de controle informando que o cliente saiu

def main():
  host = ''
  port = 2000
  sv1 = Server(host, port)
  sv1.start()

if __name__ == '__main__':
  main()