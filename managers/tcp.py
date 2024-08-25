"""
this is able to control smart/tty shells via websockets

every connection is managed through a different thread \
    that thread reads the socket continously and echos whatver it recieves to the websocket in json format
    for example, `{"uid-of-client": "command-output\n"}`
    the thread also copies the most recent read into a dictionary called 'recievedData', where any 'fifo' requests will get their output from

if your reading this as an example for your own protocol manager, here is what you are supposed to do:

0.9. MAKE A DUMB SHELL FIRST!! e.g. no fancy reads, just FIFO stuff

1. save the websock variable that is passed as a parameter to you in `startServer` - you will need that
1.1. create a dictionary that's accessible by all functions - the recieved data will be cached/stored here - in our case it'll be called `yourdatadictionary`
2. once you get a connection, create a new thread that's constantly reading that connection
3. when that thread gets data, make it send that data over the websock with the connection's uid in JSON format, aswell as saving that to dictionary said in step 1.1

4. in the run function, BEFORE YOU SEND ANY DATA, do `yourdatadictionary[uidofclient] = None` - aka just clear what you had saved
4.1. once you cleared what you have, send the command you want to execute over the socket
4.2. once sent, make a `while True` loop waiting for `yourdatadictionary[uidofclient]` to not be `None`
4.3. once `yourdatadictionary[uidofclient]` is not `None`, simply `return yourdatadictionary[uidofclient]`

doing all that allows you to have a practically unbreakable smart shell
"""

import re
import socket
import threading
import time
from managers.__base__ import BaseManager
from uuid import uuid4
from core.printl import *

connections = {}
wsock = None

class CatwalkTCP(BaseManager):
    def startServer(websock) -> None:
        """Required."""
        global connections, sock, recievedData, wsock, mostRecentlyRanCommands

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", 7763))
        sock.listen(5)

        wsock = websock
        recievedData = {}
        mostRecentlyRanCommands = []

        threading.Thread(target=CatwalkTCP.serverThread, daemon=True).start()

    def run(command:str, uuid:str, isAsync:bool) -> str:
        """Required."""
        global connections

        client = connections.get(uuid)

        if client == None:
            return "Client key \"{}\" is invalid.".format(uuid)
        
        recievedData[uuid] = None
        mostRecentlyRanCommands.append((command+'\n'))
        client["socket"].sendall((command+'\n').encode('ascii'))

        if isAsync:
            return True

        while recievedData[uuid] == None:
            time.sleep(.01)
        
        return recievedData[uuid].strip()
        
    def listening() -> tuple:
        """Required."""

        return sock.getsockname()

    def generateID() -> str:
        """Required."""
        return str(uuid4())

    def getConnections() -> dict:
        """
        Required. Must be returned in a dictionary.
        "run" must be the function to run commands. In our case, it's `CatwalkTCP.run` 

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
                "run": CatwalkTCP.run
            }

            uid = CatwalkTCP.generateID()
            connections[uid] = clientInfo
            threading.Thread(target=CatwalkTCP.readThread, args=(cs, uid)).start()

    def readThread(sock:socket.socket,uuid:str):
        """auto read data from sock"""
        global recievedData

        recievedData[uuid] = []
        
        while True:
            try:
                data = sock.recv(16384)
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
                
                print(dataline)
                recievedData[uuid] = dataline
            