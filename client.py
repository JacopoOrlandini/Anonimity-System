
import socket
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import AES


#Chiave pubblica del proxy
proxy_public_key = "";

#Generate private and public keys
random_generator = Random.new().read
private_key = RSA.generate(1024, random_generator)
public_key = private_key.publickey()

proxy = socket.socket()
host = "127.0.0.1"
port = 10000
proxy.connect((host, port))
proxy.sendall("Client: OK")

#Receive public key string from server
data = proxy.recv(1024)
data = data.replace("public_key=", '')
data = data.replace("\r\n", '')

#Convert string to key
proxy_public_key = RSA.importKey(data)

proxy.send("encrypted_message="+public_key.exportKey()+"\n")

data = proxy.recv(1024)
encrypted = eval(data)
decrypted = private_key.decrypt(encrypted)
#print decrypted

###AVVIO COMUNICAZIONE PRIVATA

#Symmetric encryption AES 
key,iv,mode = decrypted.split(",")
if mode == "CFB":
	mode = AES.MODE_CFB
	print "rilevato chiave,iv,mode"

cipher = AES.new(key, mode, iv)
while 1:
	mess = raw_input("inserire messaggio : ")

	if mess == "Stop":
		flag= 1
	else: flag = 0	
	mess = cipher.encrypt(str(mess))
	encrypted_msg = proxy_public_key.encrypt(mess, 32)
	proxy.sendall(str(encrypted_msg))
	if flag: break
	data = proxy.recv(1024)
	if not data: break;
	data = data.replace("\r \n",'')
	enc_pub_proxy = eval(data)
	dec_pub_client = private_key.decrypt(enc_pub_proxy)
	cleartext = cipher.decrypt(dec_pub_client)
	print "Server ha scritto: " + cleartext

print "Client Stopped"
proxy.close()
