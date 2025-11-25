import socket

def getConfig():
    f = open('/etc/vigil/agent.conf', 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        if not line.startswith("#") or line.strip() == "":
            lineSplit = line.split("=")
            if lineSplit[0] == "manager_ip":
                global managerIP; managerIP = lineSplit[1].strip()
            elif lineSplit[0] == "manager_port":
                global managerPort; managerPort = int(lineSplit[1].strip())
def main():
    getConfig()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", managerPort))
    s.listen(5)
    print("Vigil agent listener started on port: " + str(managerPort))
    while True:
        conn, addr = s.accept()
        if addr is not managerIP:
            conn.close()
            continue
        data = conn.recv(1024)
        command = data.decode("utf-8").strip()
        if command == "status":
            pass # Pending status implementation

main()