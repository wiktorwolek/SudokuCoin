import threading
import argparse

from P2P import *
from SudoCoin import *

chain = BlockChain()
def getJsonChain():
    return chain.toJSON()
def getInitialMessage():
    return chain.toJSON()
if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Simple P2P Network")
    parser.add_argument("--port", type=int, required=True, help="Port number to listen on")
    parser.add_argument("--peers", type=str, nargs='*', help="List of peers to connect to in format host:port")

    args = parser.parse_args()
    host = '127.0.0.1'  # You can change this to the actual IP address if running on different machines
    port = args.port

    # Start the server
    server_thread = threading.Thread(target=start_server, args=(host, port,getInitialMessage))
    server_thread.start()

    # Connect to multiple peers
    if args.peers:
        for peer in args.peers:
            try:
                peer_host, peer_port = peer.split(":")
                peer_conn = connect_to_peer(peer_host, int(peer_port))
                print(f"[CLIENT] Connected to {peer_host}:{peer_port}")
                # Start a thread to send messages to each peer
                #threading.Thread(target=send_message, args=(peer_conn,)).start()
            except Exception as e:
                print(f"[ERROR] Failed to connect to peer {peer}: {e}")

    # Wait for the server thread to finish
    server_thread.join()
    print(f"[INFO] Peer-to-peer network shutdown complete.")