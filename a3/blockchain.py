import json, hashlib, threading, time, os
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'sub-c-724199a5-6c82-4137-ae22-43db6e4e5d44'
pnconfig.publish_key = 'pub-c-4d82204f-37a8-4cf8-8248-129197d14531'

def my_publish_callback(envelope, status):
    if not status.is_error():
        pass
    else:
        pass
class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass
        elif status.category == PNStatusCategory.PNConnectedCategory:
            pass
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
    def message(self, pubnub, message):
        print(message.message)
class Person:
    def __init__(self,name1,name2,blk0,nonce):
        self.name1 = name1
        self.name2 = name2
        self.blk0 = blk0
        self.nonce = nonce
        pnconfig.user_id = name1
        self.pubnub = PubNub(pnconfig)
        self.pubnub.add_listener(MySubscribeCallback())
        self.pubnub.subscribe().channels("Channel-"+name1).execute()
    def create(self,blknum,transaction):
        if(blknum==1):
            fr = open(str(blknum-1)+".json","r")
        else:
            fr = open(self.name1+str(blknum-1)+".json","r")
        preblk = fr.read() #read and store prev block
        fr.close()
        prehash = hashlib.sha256(preblk.encode()).hexdigest() #create hash for current block
        nonce = self.nonce
        cond = True
        while(cond):
            blk = json.dumps({'Block number':blknum,'Hash':prehash,'Transaction':transaction,'Nonce':nonce,'Time':time.time(),'Mined by':self.name1},sort_keys=True,indent=4,separators=(',',': ')) #write current block
            hashout = hashlib.sha256(blk.encode()).hexdigest()
            if int(hashout[0:8],16) <= int("00000fff",16): # 5 0s: 20 bits
                cond = False
            nonce += 1
        self.blk = blk
        self.pubnub.publish().channel('Channel-'+self.name2).message(blk).pn_async(my_publish_callback)
    def write(self,blknum,blk):
        fw = open(self.name1+str(blknum)+".json","w+") #write in current block w respective blocknum name
        fw.write(blk)
        fw.close()
    def verify(self,blknum,blk):
        if(blknum==1):
            fr = open(str(blknum-1)+".json","r")
        else:
            fr = open(self.name1+str(blknum-1) + ".json", "r")
        prevHash = hashlib.sha256((fr.read()).encode()).hexdigest()
        fr.close()
        currentBlk = json.loads(blk)
        if currentBlk["Hash"] == prevHash:
            print("Block is verified by "+self.name1)
            return True
        else:
            print(self.name1 + ": Block is not verified and will be discarded.")
            return False
    def teardown (self):
        self.pubnub.unsubscribe_all()
        self.pubnub.stop()

transactions = [ "[3, 4, 5, 6]", "[4, 5, 6, 7]", "[5, 6, 7, 8]", "[6, 7, 8, 9]", "[7, 8, 9, 10]", "[8, 9, 10, 11]", "[9, 10, 11, 12]", "[10, 11, 12, 13]", "[11, 12, 13, 14]", "[12, 13, 14, 15]", "[13, 14, 15, 16]"]
blknum = 0
blk0 = json.dumps({'Block number':0,'Hash':'Genesis','Transaction':'','Nonce':0,'Time':time.time()},sort_keys=True,indent=4,separators=(',',': '))
fw = open("0.json", "w+")
fw.write(blk0)
fw.close()
alice = Person("Alice","Bob",blk0,0)
bob = Person("Bob","Alice",blk0,1000000000)

for i in transactions: #breaking out each entry in arr
    blknum += 1
    print("---Mining block no. " + str(blknum)+"---")
    verified=False
    while(verified==False):
        thread1 = threading.Thread(target=alice.create,args=(blknum,i))
        thread2 = threading.Thread(target=bob.create,args=(blknum,i))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        time.sleep(1)
        blkAlice = json.loads(alice.blk)
        blkBob = json.loads(bob.blk)
        if(blkAlice['Time']<blkBob['Time']):
            print("Alice's time: "+str(blkAlice['Time']))
            print("Bob's time: "+str(blkBob['Time']))
            print("Alice came first.")
            fasterBlk = alice.blk
            slowerBlk = bob.blk
        else:
            print("Alice's time: "+str(blkAlice['Time']))
            print("Bob's time: "+str(blkBob['Time']))
            print("Bob came first.")
            fasterBlk = bob.blk
            slowerBlk = alice.blk
        aliceVerify = alice.verify(blknum,fasterBlk)
        bobVerify = bob.verify(blknum,fasterBlk)
        if(aliceVerify and bobVerify):
            alice.write(blknum,fasterBlk)
            bob.write(blknum,fasterBlk)
            verified=True
        else:
            aliceVerify = alice.verify(blknum,slowerBlk)
            bobVerify = bob.verify(blknum,slowerBlk)
            if(aliceVerify and bobVerify):
                alice.write(blknum,slowerBlk)
                bob.write(blknum,slowerBlk)
                verified=True
            else:
                print("Both generated blocks are unverifiable. Generating new blocks...")

print("Mining complete, shutting down the channel...")
os._exit(0)