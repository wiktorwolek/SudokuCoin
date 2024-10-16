import threading
import argparse
from HttpClient import runServer
from P2P import *
from SudoCoin import *

nodeInitialized = False
chain = BlockChain()
def getJsonChain():
    return chain.toJSON()
def getInitialMessage():
    return json.dumps({"messagetype" : "initialChain" , "payload" : chain.toJSON()})


def httpRequestHandler(msg):
    print(msg)

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
    http_thread = threading.Thread(target=runServer,args=(port+1000,httpRequestHandler,))
    http_thread.start()
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
                #threading.Thread(target=send_message, args=(peer_conn,)).start()
            except Exception as e:
                print(f"[ERROR] Failed to connect to peer {peer}: {e}")

    # Wait for the server thread to finish
    server_thread.join()
    http_thread.join()
    print(f"[INFO] Peer-to-peer network shutdown complete.")