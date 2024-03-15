from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import binascii, random, sys

count = 0
M = int(sys.argv[1])
N = int(sys.argv[2])
tmp_keyArr = []
if(M>N):
    print("Please enter a number smaller than or equal to the number of public keys.")
else:
    fileSPK = open("scriptPubKey.txt","wb")
    fileSPK.write(binascii.hexlify(str(N).encode())) #writing in OP_N
    fileSPK.write(b'\n')
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
    param = [param_key.p, param_key.q,param_key.g]
    while (count<N): #generate public key N times
        key = DSA.generate(1024,domain=param)
        pubkey = key.publickey().export_key()
        tmp_keyArr.append(key)
        #write hex of public key
        fileSPK = open("scriptPubKey.txt","ab")
        fileSPK.write(binascii.hexlify(str(DSA.import_key(pubkey).y).encode()))
        fileSPK.write(b"\n")
        fileSPK.close()
        count+=1
    print("Generated " + str(N) + " pairs of keys.")
    count = 0
    message = b"CSCI301 Contemporary topic in security 2024"
    hash_obj = SHA256.new(message)
    min = 0
    max = N-M
    fileSS = open("scriptSig.txt","wb")
    fileSS.write(binascii.hexlify(str(M).encode())) #writing in OP_M
    fileSS.write(b'\n')
    while (count<M): #generate signatures M times
        if M!=N:
            if (M>1) and (min!=max):
                i = random.randrange(min,max)
            elif min==max:
                i = min
            else:
                i = 0
        else:
            i = count
        signer = DSS.new(tmp_keyArr[i], 'fips-186-3')
        signature = signer.sign(hash_obj)
        #write hex of signature
        signature_hex = binascii.hexlify(signature)
        fileSS = open("scriptSig.txt","ab")
        fileSS.write(signature_hex)
        fileSS.write(b"\n")
        fileSS.close()
        min = i+1
        count+=1
        if (max+i)<(N-M+count):
            max+=i
        else:
            max = N-M+count
    print("Generated " + str(M) + " signatures.")