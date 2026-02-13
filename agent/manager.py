import os
import threading
import signal
from systemd.daemon import notify
from time import sleep
import subprocess

wd_usec = os.getenv("WATCHDOG_USEC")
interval = max(int(int(wd_usec)/2000000), 1) if wd_usec else None
stop = False
webServer = False

def handle_sigterm(signum, frame):
    global stop; stop = True

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

notify("STATUS=Starting Vigil Client Manager…")

def pump():
    while not stop and interval:
        notify("WATCHDOG=1")
        sleep(interval)

threading.Thread(target=pump, daemon=True).start()

notify("STATUS=Starting agent listener...")
r2 = subprocess.Popen(["python3", "/usr/local/vigil/listener.py"])
sleep(2)
notify("STATUS=Agent listener started with PID: {}".format(r2.pid))

notify("STATUS=Checking extra services...")
possiblePaths = [
        "/var/log/nginx/access.log",
        "/var/log/apache2/access.log",
        "/var/log/httpd/access.log",
        "/usr/local/var/log/nginx/access.log",
        "/usr/local/var/log/apache2/access.log",
    ]
for path in possiblePaths:
    try:
        f = open(path, "r")
        f.close()
        webServer = True
        notify("STATUS=Starting web guard for access log: {}".format(path))
        r3 = subprocess.Popen(["python3", "/usr/local/vigil/web-guard.py", path])
        sleep(2)
        notify("STATUS=Web guard started with PID: {}".format(r3.pid))
    except:
        continue
if not webServer:
    notify("STATUS=No web server access logs found, skipping web-guard.")

notify("STATUS=Starting local agent...")
r = subprocess.Popen(["python3", "/usr/local/vigil/core.py"])
sleep(2)
notify("STATUS=Local agent started with PID: {}".format(r.pid))

notify("STATUS=Vigil Client Manager is running.")
notify("READY=1")

while not stop:
    sleep(1)