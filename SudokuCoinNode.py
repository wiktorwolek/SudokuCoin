import threading
import argparse
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

    nodeInitialized = False
    chain = BlockChain()       
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
        print(msg)

    def messageRecivedHandler(self,msg,conn):
        try:
            print(f"[PEER] recived message : {msg}") 
            jsonmsg = json.loads(msg)
            msgtype = jsonmsg["messagetype"]
            payload = jsonmsg["payload"]
            match msgtype:
                case "initialChain":
                    if not self.nodeInitialized:
                        print("[PEER] initializing node")
                        self.chain = BlockChain.fromJSON(payload["chain"])
                        self.nodeInitialized = self.chain.check_chain_validity()
                        print(f"[PEER] is valid chain : {self.nodeInitialized}")   
                        #miner_thread.start()
                    else:
                        host = payload["host"]
                        port = payload["port"]
                        print(f"[PEER] adding backup host {host}:{port}")
                        register_backup(payload["host"],payload["port"])
                    
                case "Transaction":
                    print("Sending transaction")
                    transaction = payload
                    self.chain.new_data(payload['sender'], payload['recipient'], payload['transaction'])
                    print(f"Added transaction: {transaction}")
                    return True

                case "newBlock":
                    print("Sending new block to chain")
                    block = payload["block"]
                    new_block = Block.fromJSON(block)
                    if self.chain.check_validity(new_block, self.chain.latest_block):
                        self.chain.chain.append(new_block)
                        print(f"Added new block: {new_block}")
                        return True
                    else:
                        print("Invalid block received")
                        return False

        except Exception as ex:
            print("Exception")
            print(ex)

    def handleMinerThread(self):
        print("Miner to work")
        block = self.chain.block_mining(str(self.user_wallet.public_key))
        print(self.chain.check_chain_validity())
        broadcast(self.send_new_block(self.host,self.port,self.user_wallet, block),"")



    def main(self):
    # Argument parsing
        parser = argparse.ArgumentParser(description="Simple P2P Network")
        parser.add_argument("--port", type=int, required=True, help="Port number to listen on")
        parser.add_argument("--peers", type=str, nargs='*', help="List of peers to connect to in format host:port")
        parser.add_argument("--password", type=str, nargs='*', help="wallet password")
        args = parser.parse_args()
        self.host = '127.0.0.1'  # You can change this to the actual IP address if running on different machines
        self.port = args.port
        self.user_wallet = Wallet(self.port,str(args.password))
        self.http_thread = threading.Thread(target=runServer,args=(self.port+1000,self.httpRequestHandler,))
        self.http_thread.start() 
        self.server_thread = threading.Thread(target=start_server, args=(self.host, self.port, self.getInitialMessage, self.messageRecivedHandler))
        self.server_thread.start()
        self.miner_thread = threading.Thread(target=self.handleMinerThread, args=())
        self.nodeInitialized = False
        if not args.peers:
            print("[SERVER] Initial node")
            self.nodeInitialized = True;
            self.chain.construct_genesis()
            self.miner_thread.start()
        # Connect to multiple peers
        if args.peers:
            for peer in args.peers:
                try:
                    peer_host, peer_port = peer.split(":")
                    peer_conn = connect_to_peer(peer_host, int(peer_port), self.messageRecivedHandler)
                    print(f"[CLIENT] Connected to {peer_host}:{peer_port}")
                    #threading.Thread(target=send_message, args=(peer_conn,)).start()
                except Exception as e:
                    print(f"[ERROR] Failed to connect to peer {peer}: {e}")
        print("hello")

        # Wait for the server thread to finish
        #server_thread.join()
        self.http_thread.join()
        print(f"[INFO] Peer-to-peer network shutdown complete.")
if __name__ == "__main__": 
    SudokuCoinNode().main();