#!/usr/env/python3
import socket
import os

def parseConf():
    conf = ["127.0.0.1", 5678]
    f = open('/etc/vigil.conf', 'r')
    confContents = f.read()
    confContentsSplit = confContents.split('\n')
    for line in confContentsSplit:
        if not line[0] == '#':
            if line.split('=')[0] == 'bind_ip':
                conf[0] = line.split('=')[1][1:-1]
            elif line.split('=')[0] == 'bind_port':
                conf[1] = line.split('=')[1]
    return conf
def spawnHandler(ip, message):
    pid = os.fork()
    if pid > 0:
        # Parent returns immediately; 'pid' is the first child's PID (not the final worker)
        sys.stdout.write("Spawned handler PID %d\n" % pid)
        return pid

    # First child
    os.setsid()          # new session, detach from TTY
    pid2 = os.fork()
    if pid2 > 0:
        # First child exits; grandchild gets re-parented to init/systemd
        os._exit(0)

    # Grandchild: become the daemonized worker
    try:
        os.chdir("/")
        os.umask(0)

        # Close inherited FDs (except stdio). Redirect stdio to /dev/null.
        try:
            maxfd = os.sysconf("SC_OPEN_MAX")
        except (AttributeError, ValueError):
            maxfd = 256
        for fd in range(3, maxfd):
            try: os.close(fd)
            except OSError: pass

        devnull = os.open("/dev/null", os.O_RDWR)
        os.dup2(devnull, 0)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)

        cmd = ("python3", "/usr/local/vigil/handler.py", ip, message)
        os.execvp(cmd[0], cmd)
    except Exception as e:
        os.write(2, ("exec failed: %s\n" % e).encode("utf-8"))
        os._exit(127)

def run():
    config = parseConf() # config returns as [{bindIP}, {bindPort}]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((config[0], int(config[1])))
    sock.listen(5)
    print('Vigil listener started on ' + config[0] + ':' + str(config[1])'.')
    while True:
        # Accept a connection
        conn, addr = sock.accept()
        agent = addr[0]  # IP address of the connecting agent
        data = conn.recv(4096)
        if data:
            message = data.decode(errors="ignore")
            spawnHandler(agent, message)
        conn.close()
run()