import os
import sys
import argparse

def printHelp():
    print("""
Vigil Installer
----------------
Usage: vigilInstall [option]
          
Options:
    -h, --help      Show this help message and exit
    -c, --client    Install only Vigil agent to the system
    -s, --server    Install Vigil manager and agent to the system
""")

def beginClientInstall():
    print("Beginning Vigil agent installation", flush=True)
    if os.path.exists('/usr/local/vigil'):
        print("Vigil appears to already be installed. If this is an error, remove /usr/local/vigil, then try again.", flush=True)
        exit(1)
    os.system('mkdir -p /usr/local/vigil')
    os.system('mkdir -p /root/quarantined_services')
    os.rename('./vigil.conf', '/etc/vigil.conf')
    os.rename('./core.py', '/usr/local/vigil/core.py')
    os.rename('./configCheck.py', '/usr/local/vigil/configCheck.py')
    os.rename('./vigil-manager.service', '/etc/systemd/system/vigil.service')
    os.system('systemctl daemon-reload')
    os.system('systemctl enable vigil.service')
    os.system('systemctl start vigil.service')

if not os.geteuid() == 0:
    print("This script must be run as root.", flush=True)
    exit(1)

if (len(sys.argv) == 1):
    printHelp()
    exit(0)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-h', '--help', action='store_true')
parser.add_argument('-c', '--client', action='store_true')
parser.add_argument('-s', '--server', action='store_true')
args = parser.parse_args()
if args.help:
    printHelp()
    exit(0)
if args.client and args.server:
    print("Please specify only one of --client or --server.", flush=True)
    exit(1)
if not args.client and not args.server:
    print("Please specify one of --client or --server.", flush=True)
    exit(1)
if args.client:
    beginClientInstall()
elif args.server:
    print("NOT IMPLEMENTED", flush=True)