from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes
from os import listdir
from os.path import isfile, join
from glob import glob

#read list of files to encrypt
files = [f for f in listdir(".") if isfile(join(".", f))] #dont hardcode filepath
txtfiles = []
for f in files:
    if f in glob("*.txt"):
        txtfiles.append(f)
print("List of text files to read: ")
for f in txtfiles:
    print(f)

#generate 2 pairs of public/private keys
key = RSA.generate(2048)
private_key = key.export_key()
file_out = open("private1.pem", "wb")
file_out.write(private_key)
file_out.close()
public_key = key.publickey().export_key()
file_out = open("receiver1.pem", "wb")
file_out.write(public_key)
file_out.close()
file_out = open("private2.pem", "wb")
file_out.write(private_key)
file_out.close()
public_key = key.publickey().export_key()
file_out = open("receiver2.pem", "wb")
file_out.write(public_key)
file_out.close()

#extract file contents
file_contents = []
for t in txtfiles:
    file = open(t,'rb')
    content = file.read()
    file_contents.append(content)
    file.close()

#encryption
print("Encrypting files...")
iv_arr = []
ct_arr = []
sym_key = get_random_bytes(16)
recipient_pkey = RSA.import_key(open("receiver1.pem").read())
file_out = open("encrypted_data.bin", "wb")
cipher_rsa = PKCS1_OAEP.new(recipient_pkey)
enc_symkey = cipher_rsa.encrypt(sym_key)
file_out.write(enc_symkey)
file_out.close()

for i in range(len(file_contents)):
    cipher = AES.new(sym_key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(file_contents[i], AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')
    key = b64encode(sym_key).decode('utf-8')
    iv_arr.append(iv)
    ct_arr.append(ct)
    file = open(txtfiles[i] + ".encrypted",'w')
    file.write(iv + "\n" + ct)
    file.close()

pause = input("Encryption of file contents complete, press ENTER to continue.")

#decryption
print("Decrypting files...")
file_in = open("encrypted_data.bin", "rb")
receiver_pkey = RSA.import_key(open("private1.pem").read())
enc_symkey = file_in.read(receiver_pkey.size_in_bytes())
cipher_rsa = PKCS1_OAEP.new(receiver_pkey)
sym_key = cipher_rsa.decrypt(enc_symkey)
file_in.close()

for i in range(len(file_contents)):
    try:
        iv = b64decode(iv_arr[i]) #insert upd iv and ct values, they shd not be inserted by copy&paste
        ct = b64decode(ct_arr[i]) #they can be written to enc file/hardcoded
        cipher = AES.new(sym_key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        print("The message was: ", pt)
        file = open(txtfiles[i] + ".decrypted",'w')
        file.write(pt.decode('utf-8'))
        file.close()
    except ValueError:
        print("Incorrect decryption")
