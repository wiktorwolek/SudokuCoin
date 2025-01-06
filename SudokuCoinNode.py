import threading
import ctypes
import argparse
import traceback
from HttpClient import runServer
from P2P import *
from SudoCoin import *
from Wallet import Wallet
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA512
from base64 import b64decode, b64encode


class SudokuCoinNode:
    known_hosts = {}
    lock = threading.Lock()
    nodeInitialized = False
    chain = BlockChain()
    forks = []    
    def getJsonChain(self):
        return self.chain.toJSON()

    def getInitialMessage(self,host,port):
        public_key = self.user_wallet.public_key.decode('utf-8')
        return json.dumps({"messagetype" : "initialChain" , "payload" : {"chain": self.chain.toJSON(),"public_key": public_key,"host":host,"port": port}})

    def send_transaction(self,sender_host,sender_port,recipient_host,recipient_port,transaction):
        payload = {
        "sender": {"host": sender_host,
                    "port": sender_port,},
        "recipient": {"host": recipient_host,
                        "port": recipient_port,},
        "transaction" : transaction }

        message =  {"messagetype" : "Transaction" , "payload" : payload,}

        return json.dumps(message)


    def send_new_block(self,host,port, wallet, block):
        payload = {
        "host": host,
        "port": port,
        "public_key": str(wallet.public_key),
        "block": block}

        message = {"messagetype" : "newBlock" , "payload" : payload}

        return json.dumps(message)



    def signMessage(self,private_key, message):
        key = RSA.import_key(private_key)
        msg_hash  = SHA256.new(message.encode()) 

        return pkcs1_15.new(key).sign(msg_hash)

    def verifySignature(self,public_key, message, signature) -> bool:
        key = RSA.import_key(public_key)
        msg_hash = SHA256.new(message.encode())
        try:
            decoded_signature = b64decode(signature) 
            pkcs1_15.new(key).verify(msg_hash, decoded_signature)
            return True 
        except (ValueError, TypeError) as e:
            print(e)
            return False  



    def httpRequestHandler(self,msg):
        print("httpmessage "+str(msg["sender"])+str(msg["recipient"])+str(msg["quantity"])+str(msg["signature"]))
        self.chain.new_data(
            sender=str(msg["sender"]),  
            recipient=str(msg["recipient"]),
            quantity=str(msg["quantity"]), 
            signature=str(msg["signature"])
        )
        

    def messageRecivedHandler(self,msg,conn):
        try:
           # print(f"[PEER] recived message : {msg}") 
            jsonmsg = json.loads(msg)
            msgtype = jsonmsg["messagetype"]
            payload = jsonmsg["payload"]
            match msgtype:
                case "initialChain":
                    if not self.nodeInitialized:
                        print("[PEER] initializing node")
                        self.nodeInitialized = True;
                        self.chain = BlockChain.fromJSON(payload["chain"])
                        self.nodeInitialized = self.chain.check_chain_validity()
                        print(f"[PEER] is valid chain : {self.nodeInitialized}")   
                        self.miner_thread.start()
                    else:
                        host = payload["host"]
                        port = payload["port"]
                        print(f"[PEER] adding backup host {host}:{port}")
                        register_backup(payload["host"],payload["port"])
                    
                case "Transaction":
                    print("Got transaction")
                    transaction = payload
                    self.chain.new_data(payload['sender'], payload['recipient'], payload['transaction'])
                    print(f"Added transaction: {transaction}")
                    return True

                case "newBlock": 
                    print("Got new block to chain")
                    with self.lock:
                        self.printChain()
                        self.printForks()
                        block = payload["block"]
                        new_block = Block.fromJSON(block)
                        broadcast(msg,conn)
                        if self.is_evil:
                            print("I am EVIL I wont add other blocks than mine")
                            return True
                        if self.chain.check_validity(new_block, self.chain.latest_block):
                            print(f"Added new block")
                            self.stop_event.set()
                            self.chain.chain.append(new_block)
                            self.miner_thread.join()
                            self.stop_event = threading.Event()
                            self.miner_thread = threading.Thread(target=self.handleMinerThread, args=(self.stop_event,))
                            self.miner_thread.start()
                            return True
                        else:
                            print("Possible Fork")
                            for f in self.forks:
                                if BlockChain.check_validity(new_block,f[-1]):
                                    print("Fork Length increesed")
                                    f.append(new_block)
                                    return True
                            if new_block.index < len(self.chain.chain) and new_block.calculate_hash == self.chain.chain[new_block.index].calculate_hash:
                                print("block on chain")
                                return True
                            if new_block.index-1 < len(self.chain.chain) and self.chain.check_validity(new_block, self.chain.chain[new_block.index-1]):
                                print("forkDetected "+str(new_block.index))
                                self.forks.append([self.chain.chain[new_block.index-1],new_block])
                                return True
                            print(new_block.proof_no)
                            self.printChain()
                            self.printForks()
                            return False

        except Exception as ex:
            print("Exception")
            print(traceback.print_exc())
    def printForks(self):
        print("Forks:")
        for f in self.forks:
            for b in f:
                print(b.proof_no,end=" ")
            print("len="+str(f[-1].index))
        print()
    def printChain(self):
        print("Chain:")
        for b in self.chain.chain:
            print(b.proof_no,end=" ")
        print("len="+str(self.chain.latest_block.index) + " hash="+sudoku_hash(str(self.chain.chain))[0:5])
    def handleMinerThread(self,stop_event):
        signature = self.signMessage(self.user_wallet.private_key,"0"+str(self.user_wallet.public_key)+str(1))
        self.chain.new_data(
            sender="0",  
            recipient=str(self.user_wallet.public_key),
            quantity=
            1, 
            signature = str(signature)
        )
        block = self.chain.block_mining(stop_event)
        if stop_event.is_set():
            return;
        broadcast(self.send_new_block(self.host,self.port,self.user_wallet, block),"")
        for f in self.forks:
            if f[-1].index >= self.chain.latest_block.index:
                print("Current chain is fork swiching")
                if self.is_evil:
                    print("I am evil i will not switch")
                    break
                newFork = []
                while True:
                    b = self.chain.chain.pop()
                    newFork.insert(0,b)
                    if b.index == f[0].index:
                        self.chain.chain.extend(f)
                        break;
                
            elif f[-1].index + 6 < self.chain.latest_block.index:
                self.forks.remove(f)
        
        self.printChain()
        self.printForks()
        print(self.chain.check_chain_validity())
        self.miner_thread = threading.Thread(target=self.handleMinerThread, args=(self.stop_event,))
        self.miner_thread.start()


    def main(self):
        parser = argparse.ArgumentParser(description="Simple P2P Network")
        parser.add_argument("--port", type=int, required=True, help="Port number to listen on")
        parser.add_argument("--peers", type=str, nargs='*', help="List of peers to connect to in format host:port")
        parser.add_argument("--password", type=str, nargs='*', help="wallet password")
        parser.add_argument("--isEvil", type=bool, nargs='?',const=False, help="Is Evil")
        args = parser.parse_args()
        self.host = '127.0.0.1'  # You can change this to the actual IP address if running on different machines
        self.port = args.port
        self.is_evil = args.isEvil
        if self.is_evil:
            print("I am Evil");
        self.user_wallet = Wallet(self.port,str(args.password))
        self.http_thread = threading.Thread(target=runServer,args=(self.port+1000,self.httpRequestHandler,))
        self.http_thread.start() 
        self.server_thread = threading.Thread(target=start_server, args=(self.host, self.port, self.getInitialMessage, self.messageRecivedHandler))
        self.server_thread.start()
        self.stop_event = threading.Event()
        self.miner_thread = threading.Thread(target=self.handleMinerThread, args=(self.stop_event,))
        self.nodeInitialized = False
        if not args.peers:
            print("[SERVER] Initial node")
            self.nodeInitialized = True;
            self.chain.construct_genesis()
            self.miner_thread.start()
        if args.peers:
            for peer in args.peers:
                try:
                    peer_host, peer_port = peer.split(":")
                    peer_conn = connect_to_peer(peer_host, int(peer_port), self.messageRecivedHandler)
                    print(f"[CLIENT] Connected to {peer_host}:{peer_port}")
                except Exception as e:
                    print(f"[ERROR] Failed to connect to peer {peer}: {e}")
        print("hello")

        # Wait for the server thread to finish
        #server_thread.join()
        self.http_thread.join()
        print(f"[INFO] Peer-to-peer network shutdown complete.")
if __name__ == "__main__": 
    SudokuCoinNode().main();