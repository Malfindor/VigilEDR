#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "Must be run as root" 
   exit 1
fi
repo_root=$(git rev-parse --show-toplevel)
# Help menu function
show_help() {
    cat <<EOF
Usage: $0 [OPTION] [ARGS]

Options:
  -h, --help           	   Show this help menu
  -s, --server             Install as a management server
  -a, --agent <IP> <PORT>  Install as an agent (requires manager IP and port)

Examples:
  $0 --server
  $0 --agent 192.168.1.100 7777
EOF
}

# Server setup function
setup_server() {
    echo "Installing VigilEDR Management Server."
	echo "Updating/Installing dependencies..."
    sudo apt-get update -qq >/dev/null 2>&1
    sudo apt-get install -y python3 mariadb -qq >/dev/null 2>&1
	echo "Installing Vigil..."
	mkdir /usr/local/vigil
	mv $repo_root/vigil-manager.service /etc/systemd/system/vigil-manager.service
	mv $repo_root/vigil.conf /etc/vigil.conf
	mv $repo_root/listener.py /usr/local/vigil/listener.py
	mv $repo_root/handler.py /usr/local/vigil/handler.py
	mv $repo_root/configCheck.py /usr/local/bin/vigil_config_check.py
	chmod +x /usr/local/vigil/listener.py /usr/local/vigil/handler.py /usr/local/bin/vigil_config_check.py
    echo "Install complete. The manager service is known as 'vigil-manager'"
}

# Agent setup function
setup_agent() {
    local manager_ip=$1
    local manager_port=$2

    if [[ -z "$manager_ip" || -z "$manager_port" ]]; then
        echo "[!] Agent mode requires <IP> and <PORT>"
        show_help
        exit 1
    fi

    echo "[*] Setting up agent to connect to $manager_ip:$manager_port..."
    # Example: install dependencies quietly
    sudo apt-get update -qq >/dev/null 2>&1
    sudo apt-get install -y python3 -qq >/dev/null 2>&1
    echo "[+] Agent setup complete."
}

# Main logic
case "$1" in
    -h|--help)
        show_help
        ;;
    -s|--server)
        setup_server
        ;;
    -a|--agent)
        setup_agent "$2" "$3"
        ;;
    *)
        echo "[!] Unknown option: $1"
        show_help
        exit 1
        ;;
esac