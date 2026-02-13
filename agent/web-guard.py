from datetime import datetime
import os
from time import sleep
import socket
import re
import sys
import signal
import threading

webShellFlags = [r"python3?\s+-c\b", 
                 r"/bin/(ba)?sh\s+-i\b", 
                 r"nc\s+.*-e\b", 
                 r"ncat\s+.*-e\b", 
                 r"socat\s+.*EXEC\b", 
                 r"curl\s+.*sh\b", 
                 r"wget\s+.*sh\b", 
                 r"powershell\s+.*-enc\b", 
                 r"Invoke-Expression\s+.*-enc\b", 
                 r"Invoke-Expression\s+.*IEX\b",
                 r"New-Object\s+System.Net.Sockets.TCPClient\b",
                 r"UNION\s+(ALL\s+)?SELECT\b",
                 r"OR\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?",
                 r"DROP\s+(TABLE|DATABASE|SCHEMA)\b",
                 r"(INSERT|DELETE|UPDATE|MERGE)\s+",
                 r"(EXEC|EXECUTE)\s*\(",
                 r"DECLARE\s+@",
                 r"xp_cmdshell",
                 r"sp_executesql",
                 r"--\s*$|/\*.*\*/",
                 ]
stop = False

def handle_sigterm(signum, frame):
    global stop; stop = True

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

def getAccessLog(path: str) -> str:
    try:
        f = open(path, "r")
        logData = f.readlines()
        f.close()
        return logData
    except:
        return ""
def run():
    processConfigFile()
    while not stop:
        checkLog()
        checkFiles()
        sleep(5)

def checkFiles():
    pass
def checkLog(): # Note: make more efficent, currently re-reads entire file each time
    lastSize = 0
    while not stop:
        try:
            currentSize = os.path.getsize(accessLogPath)
            if currentSize > lastSize:
                f = open(accessLogPath, "r")
                f.seek(lastSize)
                newLines = f.readlines()
                f.close()
                for line in newLines:
                    for pattern in webShellFlags:
                        if re.search(pattern, line):
                            triggerAlert("Web shell pattern detected in access log: {}".format(line.strip()))
                lastSize = currentSize
        except:
            pass
        sleep(5)
def processConfigFile():
    f = open("/etc/vigil/agent.conf", "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        if not line.startswith("#") or line.strip() == "":
            lineSplit = line.split("=")
            if lineSplit[0] == "manager_ip":
                global managerIP; managerIP = lineSplit[1].strip()
            elif lineSplit[0] == "event_port":
                global eventPort; eventPort = int(lineSplit[1].strip())
def triggerAlert(alert):
    f = open("/var/log/vigil.log", "a")
    f.write('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] - ' + alert + "\n")
    f.close()
    threading.Thread(target=sendAlert, args=(alert, managerIP, eventPort), daemon=True).start()
def sendAlert(alert, managerIP, eventPort):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((managerIP, int(eventPort)))
        sock.sendall(alert.encode())
        sock.close()
    except:
        f = open("/var/log/vigil.log", "a")
        f.write('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] - ' + "Failed to send alert to manager\n")
        f.close()

if len(sys.argv) != 2:
    print("Usage: python3 web-guard.py <access_log_path>")
    exit(1)
global accessLogPath; accessLogPath = sys.argv[1]
run()