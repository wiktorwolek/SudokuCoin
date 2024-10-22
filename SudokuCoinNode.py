import threading
import argparse

from P2P import *
from SudoCoin import *
from Wallet import Wallet
from Crypto.PublicKey import RSA 
from Crypto.Signature import PKCS1_v1_5 
from Crypto.Hash import SHA512
from base64 import b64decode 

class User:
    def __init__(self, host, port, getInitialMessage, messageRecivedHandler):
        self.host = host
        self.port = port
        self.wallet = Wallet(port)
        start_server(host, port, getInitialMessage, messageRecivedHandler)

    
nodeInitialized = False
chain = BlockChain()       
def getJsonChain():
    return chain.toJSON()
def getInitialMessage():
    signature = sign_msg(chain.toJSON(), priv_key)

    return json.dumps({"messagetype" : "initialChain" , "payload" : chain.toJSON(), "signature": jakaś funkca z podpisem, })

def join_Message():
    return json.dumps({"messagetype": "request", "payloads" : send_request()})
def send_request():
    request_messege = {
        "pub_key" = pub_key
        "sig" = sinn_msg()
        "msg" = siema
    }
    return json.dumps(request_messege)
    
#jak sobie wyobraża stótkre wyysłanych wiadomości 
#w pierwszej wiadomości reguest o dołączenie do p2p 
def sign_msg(chain):
    jak linijka 109
    return jakis podpis 

def messageRecivedHandler(msg):
    try:
        jsonmsg = json.loads(msg)
        print(f"[PEER] recived message : {msg}")
        msgtype = jsonmsg["messagetype"]
        match msgtype:
            case "initialChain":
                global nodeInitialized
                if not nodeInitialized:
                    print("[PEER] initializing node")
                    chain.fromJSON(jsonmsg["payload"])
                    nodeInitialized = chain.check_chain_validity()
                    print(f"[PEER] is valid chain : {nodeInitialized}")

            case "request":
                new_user_pub = jsonmsg["payload"]
                rozbić tego jsona i jeszcze if do sprawdzneia 

    except Exception as ex:
        print(":(")
        print(ex)
    
def verify_signature(public_key, message, signature):
        key = RSA.import_key(public_key)
        print(key)
        hash = SHA256.new(message.encode())
        try:
            pkcs1_15.new(key).verify(hash, signature)
            return True 
        except (ValueError, TypeError):
            return False  
        
if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Simple P2P Network")
    parser.add_argument("--port", type=int, required=True, help="Port number to listen on")
    parser.add_argument("--peers", type=str, nargs='*', help="List of peers to connect to in format host:port")

    args = parser.parse_args()
    host = '127.0.0.1'  # You can change this to the actual IP address if running on different machines
    port = args.port

    # Start the server
    server_thread = threading.Thread(target=start_server, args=(host, port, getInitialMessage, messageRecivedHandler))
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
                threading.Thread(target=send_message, args=(peer_conn,)).start()
            except Exception as e:
                print(f"[ERROR] Failed to connect to peer {peer}: {e}")

    # Wait for the server thread to finish
    server_thread.join()
    print(f"[INFO] Peer-to-peer network shutdown complete.")