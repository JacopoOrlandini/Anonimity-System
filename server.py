
import socket
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import AES

encrypt_str = "encrypted_message="
proxy_public_key = ''

#Generate private and public keys
random_generator = Random.new().read
private_key = RSA.generate(1024, random_generator)
public_key = private_key.publickey()

#Declartion

mysocket = socket.socket()
host = "127.0.0.1"
port = 20000
mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mysocket.bind((host, port))
mysocket.listen(5)
print "SERVER waiting connection..."
proxy = socket.socket()
c, addr = mysocket.accept()


###########	CICLO CON PROXY PER SCAMBIO CHIAVI PUBBLICHE

while True:
		print "waiting data..."
		data = c.recv(1024)
		data = data.replace("\r\n", '') 
		if data == "Server: OK":
			c.send("public_key=" + public_key.exportKey()+"\n")
			print "Public key sent to client."

		elif encrypt_str in data: 
			data = data.replace(encrypt_str, '')
			proxy_public_key = RSA.importKey(data)
			break;
bla = c.recv(1024)
encrypted = eval(bla)
decrypted = private_key.decrypt(encrypted)
#print decrypted

###AVVIO COMUNICAZIONE PRIVATA

key,iv,mode = decrypted.split(",")
if mode == "CFB":
	mode = AES.MODE_CFB
	print "Ricevuto parametri chiave simmetrica"
cipher = AES.new(key, mode, iv)

while 1:
	print "Aspetto messaggio..."
	data = c.recv(1024)
	data = data.replace("\r \n",'')
	enc_pub_proxy = eval(data)
	dec_pub_client = private_key.decrypt(enc_pub_proxy)
	cleartext = cipher.decrypt(dec_pub_client)
	print "Client ha scritto : " + cleartext
	if cleartext == "Stop":break
	mess = raw_input("inserire messaggio : ")
	mess = cipher.encrypt(str(mess))
	encrypted_msg = proxy_public_key.encrypt(mess, 32)
	c.sendall(str(encrypted_msg))

print "Server Stopped"
c.close()




