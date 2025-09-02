#!/usr/env/python3
import sys
import os

bindIpPres = False
bindPortPres = False
if not os.path.exists('/etc/vigil.conf'):
    print("Config file not found. Replace or ensure that the config file is located at /etc/vigil.conf")
    sys.exit(2)
errors = []
f = open('/etc/vigil.conf', 'r')
contents = f.read()
if len(contents) == 0:
    print("Config file appears to be empty.")
    sys.exit(3)
contents = contents.split('\n')
lineNum = 0
for line in contents:
    lineNum = lineNum + 1
    if not len(line) == 0:
        if not line[0] == '#':
            if line[0] == 'bind_ip':
                bindIpPres = True
                line = line.split('=')
                if len(line[1]) == 0:
                    errors.append("Missing value for variable 'bind_ip' on line " + str(lineNum))
                elif not ((line[1][0] == '"') and (line[1][-1] == '"')):
                    errors.append("Missing quotation marks around variable 'bind_ip' on line " + str(lineNum))
            if line[0] == 'bind_port':
                bindIpPres = True
                line = line.split('=')
                if len(line[1]) == 0:
                    errors.append("Missing value for variable 'bind_port' on line " + str(lineNum))
                elif (int(line[1]) < 1) or (int(line[1]) > 65535):
                    errors.append("value out of range for variable 'bind_port' on line " + str(lineNum))

if not len(errors) == 0:
    for error in errors:
        print(error)
    sys.exit(1)