import subprocess
import time
import os

allowedUsers = []
blacklistedUsers = []
allowedIPs = []
reverseShellFlags = ["python -c", "/bin/sh -i", "/bin/bash -i", "nc .* -e", "ncat .* -e", "socat .* EXEC"]

def run():
    while True:

        time.sleep(10)
def checkUsers():
    f = open("/etc/passwd", "r")
    users = f.readlines()
    f.close()
    for user in users:
        userSplit = user.split(":")
        if (userSplit[0] in blacklistedUsers) or ((userSplit[2] == '0') or (userSplit[3] == '0')):
            print("Blacklisted user '" + userSplit[0] + "' exists on system!", flush=True)
        elif ((not userSplit[0] in allowedUsers) and (userSplit[2] >= '1000')):
            print("Unrecognized user '" + userSplit[0] + "' exists on system!", flush=True)

def checkProcesses():
    processes = getOutputOf("ps aux")
    processesSplit = processes.split("\n")
    for process in processesSplit:
        for flag in reverseShellFlags:
            if flag in process:
                print("Potential reverse shell detected: " + process, flush=True)

def checkIPs():
    connections = getOutputOf("who")
    connectionsSplit = connections.split("\n")
    for connection in connectionsSplit:
        if len(connection) > 5:
            ipSplit = connection[4].split('.')
            if (len(ipSplit) == 4) and (connection[4] not in allowedIPs):
                user = ipSplit[0]
                seat = ipSplit[1]
                os.system('echo "These are not the machines you are looking for." | write ' + user + seat)
                date = ipSplit[2]
                time = ipSplit[3]
                remoteIP = ipSplit[4]
                print("Unrecognized IP address '" + remoteIP + "' connected to the system as user '" + user + "' on " + date + " at " + time, flush=True)

def getOutputOf(command: str):
    try:
        result = subprocess.run([command], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()

def processConfigFile():
    f = open("/etc/vigil.conf", "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        if not line.startswith("#") or line.strip() == "":
            lineSplit = line.split("=")
            if lineSplit[0] == "allowed_users":
                usersSplit = lineSplit[1].split(",")
                for user in usersSplit:
                    allowedUsers.append(user.strip()) 
            elif lineSplit[0] == "blacklisted_users":
                usersSplit = lineSplit[1].split(",")
                for user in usersSplit:
                    blacklistedUsers.append(user.strip())
            elif lineSplit[0] == "allowed_ips":
                ipsSplit = lineSplit[1].split(",")
                for ip in ipsSplit:
                    allowedIPs.append(ip.strip())