
import socket
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import AES

encrypt_str = "encrypted_message="
client_public_key = ""


####SYMMETRIC DATA
key = b'Network_security'      
#iv = Random.new().read(AES.block_size)
iv = 'This is an IV456'
mode = AES.MODE_CFB


#Generate private and public keys
random_generator = Random.new().read
private_key = RSA.generate(1024, random_generator)
public_key = private_key.publickey()


#Declaration
mysocket = socket.socket()
host = "127.0.0.1"
port = 10000
mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mysocket.bind((host, port))
mysocket.listen(50)
c, addr = mysocket.accept()


###########	CICLO CON CLIENT PER SCAMBIO CHIAVI PUBBLICHE

while True:
		data = c.recv(1024)
		data = data.replace("\r\n", '') 
		if data == "Client: OK":
			c.send("public_key=" + public_key.exportKey()+"\n")
			#print "Public key sent to client."

		elif encrypt_str in data: 
			data = data.replace(encrypt_str, '')
			data = data.replace("\r\n", '')
			#print "chaive pubblica client\n" + data
			client_public_key = RSA.importKey(data)
			message = key+','+iv+','+'CFB'
			encrypted = client_public_key.encrypt(message, 32)
			c.sendall(str(encrypted))
			break


###########	CICLO DEL SERVER PER SCAMBIO CHIAVI PUBBLICHE

proxy = socket.socket()

port = 20000
proxy.connect((host, port))
proxy.sendall("Server: OK")
data = proxy.recv(1024)
data = data.replace("public_key=", '')
data = data.replace("\r\n", '')
server_public_key = RSA.importKey(data)
proxy.send("encrypted_message="+public_key.exportKey())

message = key+','+iv+','+'CFB'
encrypted = server_public_key.encrypt(message, 32)
proxy.sendall(str(encrypted))


###########################################



###AVVIO COMUNICAZIONE

print "Running Anonymity System..."
while 1:
	data = c.recv(1024) 
	enc_pub_client = eval(data) 
	dec_pub_client = private_key.decrypt(enc_pub_client)
	enc_pub_server = server_public_key.encrypt(dec_pub_client, 32)
	proxy.send(str(enc_pub_server)+'\n')
	data = proxy.recv(1024)
	if not data: break;
	enc_pub_server = eval(data)
	dec_pub_server = private_key.decrypt(enc_pub_server)
	enc_pub_client = client_public_key.encrypt(dec_pub_server, 32)
	c.send(str(enc_pub_client)+'\n')

print "Proxy stopped"
c.close()


