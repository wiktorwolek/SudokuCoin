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
    
known_hosts = {}

nodeInitialized = False
chain = BlockChain()       
def getJsonChain():
    return chain.toJSON()

def getInitialMessage(private_key,port):
    message = 'Initial Message'
    signature = b64encode(signMessage(private_key,message)).decode('utf-8')
   # public_key_base64 = b64encode(public_key).decode('utf-8')
    public_key = public_key.decode('utf-8')
    return json.dumps({"messagetype" : "initialChain" , "payload" : {"chain":chain.toJSON(), "signature": signature, "public_key": public_key,"host":host,"port": port}})

def send_transaction(sender_host,sender_port,recipient_host,recipient_port,transaction):
    payload = {
        "sender": {"host": sender_host,
                   "port": sender_port,},
        "recipient": {"host": recipient_host,
                      "port": recipient_port,},
        "transaction" : transaction }
    
    #signature = b64encode(signMessage(private_key,payload)).decode('utf-8')

    message =  {"messagetype" : "Transaction" , "payload" : payload,}# "signature": signature,}

    return json.dumps(message)


def send_new_block(host,port, wallet, block):
        payload = {
        "host": host,
        "port": port,
        "public_key": wallet.public_key,
        "body": 'Sending new block',
        "blockchain": block}

        message = {"messagetype" : "newBlock" , "payload" : payload}

        return json.dumps(message)



def signMessage(private_key, message):
    key = RSA.import_key(private_key)
    msg_hash  = SHA256.new(message.encode()) 

    return pkcs1_15.new(key).sign(msg_hash)

def verifySignature(public_key, message, signature) -> bool:
        key = RSA.import_key(public_key)
        msg_hash = SHA256.new(message.encode())
        try:
            decoded_signature = b64decode(signature) 
            pkcs1_15.new(key).verify(msg_hash, decoded_signature)
            return True 
        except (ValueError, TypeError) as e:
            print(e)
            return False  



def httpRequestHandler(msg):
    print(msg)

def messageRecivedHandler(msg,conn):
    try:
        print(f"[PEER] recived message : {msg}") 
        jsonmsg = json.loads(msg)
        msgtype = jsonmsg["messagetype"]
        payload = jsonmsg["payload"]
        match msgtype:
            case "initialChain":
                global nodeInitialized
                if not nodeInitialized:
                    print("[PEER] initializing node")
                    chain.fromJSON(payload["chain"])
                    nodeInitialized = chain.check_chain_validity()
                    print(f"[PEER] is valid chain : {nodeInitialized}")
                    key_pub = payload["public_key"]        
                    if verifySignature(key_pub, 'Initial Message', payload["signature"]):
                        known_hosts['host_public_key'] = key_pub
                        print("Host public key saved successfully.")
                    else:
                        print("Failed to verify signature.")

                else:
                    host = payload["host"]
                    port = payload["port"]
                    print(f"[PEER] adding backup host {host}:{port}")
                    register_backup(payload["host"],payload["port"])
                
            case "Transaction":
                print("Sending transaction")
                transaction = payload
                chain.new_data(payload['sender'], payload['recipient'], payload['transaction'])
                print(f"Added transaction: {transaction}")
                return True

            case "newBlock":
                print("Sending new block to chain")
                block = payload["block"]
                new_block = Block.fromJSON(json.dumps(block))
                if chain.check_validity(new_block, chain.latest_block):
                    chain.chain.append(new_block)
                    print(f"Added new block: {new_block}")
                    return True
                else:
                    print("Invalid block received")
                    return False

            case "chainRequest":
                response = {
                    "messagetype": "chainResponse",
                    "payload": {"chain": chain.toJSON()}
                }
                conn.send(json.dumps(response).encode('utf-8'))
                print("Sent chain to peer")
                return True

            case "chainResponse":
                new_chain = BlockChain.fromJSON(payload["chain"])
                if len(new_chain.chain) > len(chain.chain) and new_chain.check_chain_validity():
                    chain.chain = new_chain.chain
                    print("Synchronized blockchain")
                    return True
                else:
                    print("Received chain is invalid or shorter")
                    return False

    except Exception as ex:
        print("Exception")
        print(ex)
        
if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Simple P2P Network")
    parser.add_argument("--port", type=int, required=True, help="Port number to listen on")
    parser.add_argument("--peers", type=str, nargs='*', help="List of peers to connect to in format host:port")

    args = parser.parse_args()
    host = '127.0.0.1'  # You can change this to the actual IP address if running on different machines
    port = args.port
    http_thread = threading.Thread(target=runServer,args=(port+1000,httpRequestHandler,))
    http_thread.start()
    # Start the server
    user_wallet = Wallet(port)
    server_thread = threading.Thread(target=start_server, args=(host, port, getInitialMessage(user_wallet.private_key, user_wallet.public_key), messageRecivedHandler))#pozamieniać te user
    server_thread.start()
    if not args.peers:
        print("[SERVER] Initial node")
        nodeInitialized = True;
    
    # Connect to multiple peers
    if args.peers:
        for peer in args.peers:
            try:
                peer_host, peer_port = peer.split(":")
                peer_conn = connect_to_peer(peer_host, int(peer_port), messageRecivedHandler)
                print(f"[CLIENT] Connected to {peer_host}:{peer_port}")
                #threading.Thread(target=send_message, args=(peer_conn,)).start()
            except Exception as e:
                print(f"[ERROR] Failed to connect to peer {peer}: {e}")
        print("hello")

    # Wait for the server thread to finish
    server_thread.join()
    http_thread.join()
    print(f"[INFO] Peer-to-peer network shutdown complete.")