import socket
import threading
import argparse
import json

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

# Global variables to hold connections
peers = []
backuppeers = []
prevmsg = []

# Broadcast function to send a message to all peers
def broadcast(msg, sender_conn):
    msg = msg + "\n"  # Add a newline delimiter
    for peer in peers:
        if peer != sender_conn:
            try:
                peer.send(msg.encode('utf-8'))
            except Exception as ex:
                peer.close()
                peers.remove(peer)
                print(f"[PEER] disconnected {peer}")

# Server function to listen for incoming connections
def start_server(host, port, getInitialMessage, messageRecivedHandler):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[SERVER] Listening on {host}:{port}")
    while True:
        conn, addr = server.accept()
        print(f"[SERVER] Connected to {conn.getsockname()}")
        if conn.getsockname() in backuppeers:
            del backuppeers[conn.getsockname()]
        peers.append(conn)
        send_message(conn, getInitialMessage(host, port))
        threading.Thread(target=handle_peer, args=(conn, messageRecivedHandler)).start()

# Function to handle communication with a peer
def handle_peer(conn, message_recived_handler):
    buffer = ""  # Buffer to hold incomplete messages
    while True:
        try:
            data = conn.recv(1024).decode('utf-8')  # Adjust buffer size as needed
            if not data:
                break
            buffer += data  # Append incoming data to the buffer
            while "\n" in buffer:  # Process complete messages
                msg, buffer = buffer.split("\n", 1)  # Split at the first delimiter
                if msg and msg not in prevmsg:
                    prevmsg.insert(0, msg)
                    message_recived_handler(msg, conn)
                    broadcast(msg, conn)
        except Exception as ex:
            print(f"[SERVER] disconnected: {ex}")
            conn.close()
            if backuppeers:
                backup = backuppeers.pop()
                connect_to_peer(backup[0], backup[1], message_recived_handler)
            break

# Register a backup peer
def register_backup(host, port):
    for peer in peers:
        if peer.getsockname() == (host, port):
            return
    backuppeers.append((host, port))

# Client function to connect to a peer
def connect_to_peer(host, port, messageRecivedHandler):
    try:
        print(f"[SERVER] connecting to {host}:{port}")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        peers.append(client)
        threading.Thread(target=handle_peer, args=(client, messageRecivedHandler)).start()
        return client
    except Exception as ex:
        print(f"[SERVER] error connecting to {host}:{port} exception {ex}")

# Function to send messages to peers
def send_message(conn, msg):
    msg = msg + "\n"  # Add a newline delimiter
    conn.send(msg.encode('utf-8'))
