import socket
import sys
import random
import time
import threading

die = False
threads = []
routines = [
    [
        "bash",
        "server-%%",
        "-randMac",
        "192.168.0.1",
        "x64"
    ],
    [
        "\n",
        "DESKTOP-%%",
        "someone",
        "-randMac",
        "192.168.0.1",
        "x64"
    ]
]

def genRandomMac():
    hexStr = "0123456789abcdef"
    try:
        oui = random.choice(open("fakeclioui.txt", "r", encoding="utf-8").read().split("\n")).split("=", 1)[0]
    except:
        oui = random.choice(["747548", "3495DB", "B4CEF6", "60A44C", "843838"])
        
    sr = ""

    for x in range(3):
        sr += ''.join([random.choice(hexStr) for _ in range(2)])
    
    mac = ""
    combo = [x for x in (oui + sr)]

    for x in combo.copy():
        mac += ''.join(combo[:2]) + ":"
        try:
            combo.pop(0)
            combo.pop(0)
        except:
            break

    return ''.join(mac[:17])

def listener(sock):
    routine = random.choice(routines)
    for x in routine:
        if x == "-randMac":
            x = genRandomMac()
        x = x.replace("%%", ''.join([random.choice("ABCDEFGHIJKLMNOPQRSTUVXWYZ") for _ in range(6)]))
            
        print("<<< " + sock.recv(1024).decode("ascii").strip())
        print(">>> " + x)
        sock.sendall(x.encode("ascii"))

    while True:
        try:
            try:
                data = sock.recv(2048 * 16).decode('ascii').strip()
            except:
                if die:
                    return
                continue

            if data:
                if data == "exit":
                    return
                elif data == "echo 1":
                    sock.sendall("1".encode('ascii'))
                    continue

                print(data)

            sock.sendall("i am not real ".encode('ascii'))
        except TimeoutError:
            return
        except:
            pass

for x in range(int(sys.argv[2])):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect(("127.0.0.1", int(sys.argv[1])))

    print("-" * 25)

    print("sock now managed by new thread")

    #s.settimeout(None)
    threads.append(threading.Thread(target=listener, args=(s,), daemon=True))
    threads[-1].start()

    print("-" * 25)

print("waiting for last thread to finish...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    die=True
    threads[-1].join()