import socket
import threading
import argparse
# Global variable to hold connections
peers = []

# Server function to listen for incoming connections
def start_server(host, port, getInitialMessage,messageRecivedHandler):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[SERVER] Listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        print(f"[SERVER] Connected to {addr}")
        peers.append(conn)
        send_message(conn, getInitialMessage())
        threading.Thread(target=handle_peer, args=(conn,messageRecivedHandler)).start()

# Function to handle communication with a peer
def handle_peer(conn,message_recived_handler):
    while True:
        try:
            msg = conn.recv(1024).decode('utf-8')
            if msg:
                message_recived_handler(msg)
                # Send the message to all connected peers
                broadcast(msg, conn)
        except:
            conn.close()
            break

# Broadcast function to send a message to all peers
def broadcast(msg, sender_conn):
    for peer in peers:
        if peer != sender_conn:
            try:
                peer.send(msg.encode('utf-8'))
            except:
                peer.close()
                peers.remove(peer)

# Client function to connect to a peer
def connect_to_peer(host, port,messageRecivedHandler):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    threading.Thread(target=handle_peer, args=(client,messageRecivedHandler)).start()
    return client

# Function to send messages to peers
def send_message(conn, msg):
    conn.send(msg.encode('utf-8'))
