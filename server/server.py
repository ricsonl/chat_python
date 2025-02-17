import socket
import threading
import os.path

class Server:
  def __init__(self, host, port):
    self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)# configuracao do socket p/ troca de mensagens
    self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# configuracao do socket p/ recebimento de arquivos
    self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    self.orig = (host, port)
    self.tcp_socket.bind(self.orig)
    self.tcp_socket.listen(1)

    self.clients = {}

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
      t = threading.Thread(target=self.receive_file_from_client)
      t.start()
      
      fmt = f'INFO:{self.clients[client_udp]} enviou {wds[1]}'# mensagem formatada para envio
      print(fmt)
      for c in self.clients.keys():# para cada cliente
        if c != client_udp:
          self.udp_socket.sendto(fmt.encode(), c)# envia mensagem de controle informando que o cliente enviou o arquivo

    elif wds[0] == 'GET':
      t = threading.Thread(target=self.send_file_to_client, args=(wds[1],))
      t.start()

  def receive_file_from_client(self):
    con, client_tcp = self.tcp_socket.accept()
    filename = ''
    while True:# socket tcp recebe primeiramente o nome do arquivo
      c = con.recv(1).decode()
      if c == '\n':
        break   
      filename += c

    with open(filename, 'wb') as f:# cria arquivo com esse nome
      print(f'<-- Recebendo "{filename}" de {client_tcp}...')
      while True:# comeca a receber o arquivo
        data = con.recv(1024)
        if not data:
            break
        f.write(data)
      print('<-- Arquivo recebido')
    con.close()

  def send_file_to_client(self, filename):
    con, client_tcp = self.tcp_socket.accept()
    if os.path.isfile(f'./{filename}'):# se o arquivo existe
      with open(filename, 'rb') as f:
        print(f'--> Enviando "{filename}" para {client_tcp}...')
        con.send(f'{filename}\n'.encode())# pelo socket tcp, envia primeiramente o nome do arquivo seguido por \n
      
        l = f.read(1024)# le parte do arquivo
        while (l):# ate acabar o arquivo
          con.send(l)# envia
          l = f.read(1024)# le outra parte do arquivo
        print('--> Arquivo enviado')
    else: con.send(f'ERRO\tArquivo "{filename}" inexistente\n'.encode())
    
    con.close()

def main():
  host = ''
  port = 2000
  sv = Server(host, port)
  t = threading.Thread(target=sv.run_udp)
  t.start()

if __name__ == '__main__':
  main()