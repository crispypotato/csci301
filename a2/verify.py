from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import binascii, sys

#read the files
fileSPK = open(sys.argv[1],"r")
pkey_dump = fileSPK.read()
pkey_arr = pkey_dump.split("\n")
fileSPK.close()
fileSS = open(sys.argv[2],"r")
signature_dump = fileSS.read()
signature_arr = signature_dump.split("\n")
fileSS.close()
pkey_arr.remove("")
signature_arr.remove("")

#write into stack, then pop stack into respective variables
pkey_arr.extend(signature_arr)
stack = pkey_arr
print("All values have been combined into a stack.")
pkey_arr = []
signature_arr = []
for i in range(len(stack)):
    if i==0:
        N = int(binascii.unhexlify(stack[i]).decode())
    elif i>0 and i<=N:
        pkey_arr.append(stack[i])
    elif i==N+1:
        M = int(binascii.unhexlify(stack[i]).decode())
    else:
        signature_arr.append(stack[i])
print("Stack values split into scriptPubKey and scriptSig. Authenticating signatures...")

#verify key and signature
key_pem = "-----BEGIN PUBLIC KEY-----\n\
        MIIBtjCCASsGByqGSM44BAEwggEeAoGBAKny/js0C9Fyxgm4fKPcRmc8DA1bllbK\n\
        eGOsmDOigr/3UoMkP3PgFBmy1TflMAFpuaRjhaToyiHuIKzHWqsoSCIbNJLSdNIp\n\
        B7UYzIyMLgW18/MYP7MD03OZaHwNd3RDcdgo+PPYLCu19OVps/x529I5g5rQ1rYS\n\
        1G4X4YqzR6b/AhUAonftFtvgA+ApsoLjikJMfh9dpdMCgYA8IIfA2od8Q+Gzsivl\n\
        +l7VXlFjUfhlllU/6lG6MDKx5hU+55V77VtIFcF+9jm6OusXJNF/za/xTvqqNNf5\n\
        rir+1Fq5IFPBd5uIc56TIGh4BjNbA3zs8eKtJ2dgEou5JDmJ0OrK5O1/Uc3+Othu\n\
        JrLqJFTdMeZSAYTIyzflRcD/+AOBhAACgYBCqTwq8HUB5cwVSrwefTGuk0pYJDWb\n\
        qW1HoFpmgyBkXYdsU3rNEqDqgXaqj8erKqH14WiGMTjKvQfo3EDQseYDG+g3639q\n\
        PpvZw47kYp4GA5TH6O4cAeSHRLkapH6zrOjV2Zx7EX79oRM4VvgGhSu5Dcp6z3x/\n\
        wIrytRMgdLwauA==\n-----END PUBLIC KEY-----"
param_key = DSA.import_key(key_pem)
message = b"CSCI301 Contemporary topic in security 2024"
hash_obj = SHA256.new(message)
index_track = 0 # marks the previous matching pubkey
for i in range(M):
    signature = binascii.unhexlify(signature_arr[i])
    for j in range(N):
        if (j<=index_track) and i!=0:
            continue
        else:
            tup = [int(binascii.unhexlify(pkey_arr[j]).decode()), param_key.g, param_key.p, param_key.q]
            pub_key = DSA.construct(tup)
            verifier = DSS.new(pub_key, 'fips-186-3')
            try:
                verifier.verify(hash_obj, signature)
                print("Signature "+ str(i+1) +" matches with public key of index " + str(j))
                index_track = j
                break
            except ValueError:
                print("Signature "+ str(i+1) +" does not match with public key of index " + str(j))