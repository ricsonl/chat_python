import socket
import threading
from functools import cached_property

class Server:
  def __init__(self, host, port):
    self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)# configuracao do socket p/ troca de mensagens
    self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# configuracao do socket p/ recebimento de arquivos
    self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    self.orig = (host, port)
    self.clients = {}

  def run_tcp(self):
    self.tcp_socket.bind(self.orig)
    self.tcp_socket.listen(1)
    while True:
      con, client_tcp = self.tcp_socket.accept()
      t = threading.Thread(target=self.tcp_con_sending, args=(con, client_tcp))
      t.start()
    self.tcp_socket.close()

  def run_udp(self):
    self.udp_socket.bind(self.orig)
    print('Aguardando conexão')
    while True:
      msg, client_udp = self.udp_socket.recvfrom(1024)# recebe mensagens pelo socket udp
      self.client_msg_dec(msg, client_udp)# metodo que interpreta a mensagem recebida

    self.udp_socket.close()

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
    
    elif wds[0] == 'LIST':
      userlist = ''
      for n in self.clients.values():# para cada nome de cliente
        userlist = userlist + n + ', '
      self.udp_socket.sendto(f'INFO:{userlist[:-2]}'.encode(), client_udp)# envia a lista para o cliente que pediu
    
    elif wds[0] == 'BYE':
      fmt = f'INFO:{self.clients[client_udp]} saiu'# mensagem formatada para envio
      print(fmt)
      self.udp_socket.sendto('ok'.encode(), client_udp)# enviado para o cliente apenas para ele não ficar parado no recvfrom
      self.clients.pop(client_udp)# remove o cliente do dicionario
      for c in self.clients.keys():# para cada cliente
        self.udp_socket.sendto(fmt.encode(), c)# envia mensagem de controle informando que o cliente saiu
    
    elif wds[0] == 'FILE':
      fmt = f'INFO:{self.clients[client_udp]} enviou {wds[1]}'# mensagem formatada para envio
      print(fmt)
      for c in self.clients.keys():# para cada cliente
        if c != client_udp:
          self.udp_socket.sendto(fmt.encode(), c)# envia mensagem de controle informando que o cliente enviou o arquivo

    elif wds[0] == 'GET':
      pass

  def tcp_con_sending(self, con, client_tcp):
    with open('file', 'wb') as f:
      while True:
        print(f'Recebendo arquivo de {client_tcp}...')
        data = con.recv(1024)
        if not data:
            break
        f.write(data)
      print('Arquivo recebido')
      con.close()

def main():
  host = ''
  port = 2000
  sv = Server(host, port)
  t1 = threading.Thread(target=sv.run_tcp)
  t2 = threading.Thread(target=sv.run_udp)
  t1.start()
  t2.start()

if __name__ == '__main__':
  main()