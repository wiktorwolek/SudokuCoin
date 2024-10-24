import threading
import argparse

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

def getInitialMessage(private_key, public_key):
    message = 'Initial Message'
    signature = b64encode(signMessage(private_key,message)).decode('utf-8')
   # public_key_base64 = b64encode(public_key).decode('utf-8')
    public_key = public_key.decode('utf-8')
    return json.dumps({"messagetype" : "initialChain" , "payload" : chain.toJSON(), "signature": signature, "public_key": public_key})

# def getRequestMessage():
#     return json.dumps({"messagetype": "request", "payloads" : requestMessage()})

# def requestMessage(private_key, public_key, message):
#     signature = b64encode(sign_message(private_key,message)).decode('utf-8')
#     request_messege = {
#         "public_key": public_key, 
#         "signature": signature,
#         "message" : "Hello!!!",
#     }
#     return json.dumps(request_messege)

"""
ujednolicić wiadomości 
"""
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


#jak sobie wyobraża stótkre wyysłanych wiadomości 
#w pierwszej wiadomości reguest o dołączenie do p2p 
# def sign_msg(chain):
#     jak linijka 109
#     return jakis podpis 

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
                    key_pub = jsonmsg["public_key"]        
                    if verifySignature(key_pub, 'Initial Message', jsonmsg["signature"]):
                        known_hosts['host_public_key'] = key_pub
                        print("Host public key saved successfully.")
                    else:
                        print("Failed to verify signature.")

            # case "request":
            #     new_user_pub = jsonmsg["payload"]
            #     rozbić tego jsona i jeszcze if do sprawdzneia 

    except Exception as ex:
        print(":(")
        print(ex)
        
if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Simple P2P Network")
    parser.add_argument("--port", type=int, required=True, help="Port number to listen on")
    parser.add_argument("--peers", type=str, nargs='*', help="List of peers to connect to in format host:port")

    args = parser.parse_args()
    host = '127.0.0.1'  # You can change this to the actual IP address if running on different machines
    port = args.port

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

    # Wait for the server thread to finish
    server_thread.join()
    print(f"[INFO] Peer-to-peer network shutdown complete.")