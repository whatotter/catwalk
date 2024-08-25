# inspired by https://github.com/cytopia/pwncat?tab=readme-ov-file#at-a-glance round-robin
# same as tcp, with tiny bind modifications

import random
import re
import socket
import threading
import time
from managers.__base__ import BaseManager
from uuid import uuid4
from core.printl import *

connections = {}
wsock = None

class CatwalkRRTCP(BaseManager):
    def startServer(websock) -> None:
        """Required."""
        global connections, sock, recievedData, wsock, mostRecentlyRanCommands, IPtoIDbinds, socks, basePort, activePorts

        socks = []
        basePort = 8863
        activePorts = []
        portRanges = (9000,11000)


        for x in range(6):
            if x != 0:
                port = random.randint(portRanges[0], portRanges[1])
            else:
                port = basePort

            activePorts.append(port)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("0.0.0.0", port))
            sock.listen(5)

            socks.append(sock)

        wsock = websock
        IPtoIDbinds = {}
        recievedData = {}
        mostRecentlyRanCommands = []

        for rrsock in socks:
            threading.Thread(target=CatwalkRRTCP.serverThread, args=(rrsock,), daemon=True).start()

    def run(command:str, uuid:str, isAsync:bool) -> str:
        """Required."""
        global connections

        client = connections.get(uuid)

        if client == None:
            return "Client key \"{}\" is invalid.".format(uuid)
        
        recievedData[uuid] = None
        mostRecentlyRanCommands.append((command+'\n'))
        print('sent: {}'.format(command))
        client["socket"].sendall((command+'\n').encode('ascii'))

        if isAsync:
            return True

        while recievedData[uuid] == None:
            time.sleep(.01)
        
        return recievedData[uuid].strip()
        
    def listening() -> tuple:
        """Required."""

        return socks[0].getsockname()

    def generateID() -> str:
        """Required."""
        return str(uuid4())

    def getConnections() -> dict:
        """
        Required. Must be returned in a dictionary.
        "run" must be the function to run commands. In our case, it's `CatwalkRRTCP.run` 

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

    def serverThread(bindsock):
        """Not required."""
        global connections, activePorts

        while True:
            info("[TCP] waiting for connection")
            cs, caddr = bindsock.accept()
            info("[TCP] connection from {}".format(caddr))

            clientInfo = {
                "ip": caddr[0],
                "socket": cs,
                "run": CatwalkRRTCP.run
            }

            if cs.recv(512, socket.MSG_PEEK) == b'showenv':
                cs.recv(512) # clear ^
                cs.sendall(("env:setports {}".format(' '.join([str(x) for x in activePorts[1:]]))).encode('ascii'))

            if IPtoIDbinds.get(caddr[0], False): # IP-to-UID bind already exists - use that
                connections[IPtoIDbinds[caddr[0]]] = clientInfo
                threading.Thread(target=CatwalkRRTCP.readThread, args=(cs, IPtoIDbinds[caddr[0]])).start()

            else: # IP-to-UID bind doesn't exist
                uid = CatwalkRRTCP.generateID()
                IPtoIDbinds[caddr[0]] = uid
                connections[uid] = clientInfo
                threading.Thread(target=CatwalkRRTCP.readThread, args=(cs, uid)).start()

    def readThread(sock:socket.socket,uuid:str):
        """auto read data from sock"""
        global recievedData

        while True:
            time.sleep(0.1)
            try:
                data = sock.recv(16384)

                print(data)

                if data == b'':
                    raise ConnectionAbortedError("disconnect")
                
                datastr = data.decode('ascii')
            except:
                warn("[TCP] {} disconnected".format(uuid))
                sock.close()
                return
            
            wsock.emit('clientrx', {uuid: datastr}, namespace='/')

            # important stuff after this

            cleanANSI = re.compile(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            datalns = datastr.split('\n')

            blStrings = [
                "@", "C:\\",
                "Microsoft Windows [Version ",
                "(c) Microsoft Corporation"
            ]
            for dataline in datalns:
                dataline = cleanANSI.sub('', dataline).strip()

                for x in blStrings:
                    if x in dataline:
                        dataline = ""

                if len(mostRecentlyRanCommands) != 0 and mostRecentlyRanCommands[-1].strip() == dataline.strip():
                    continue

                if len(dataline.strip()) == 0:
                    continue
                
                print("rtn: {}".format(dataline))
                recievedData[uuid] = dataline
            