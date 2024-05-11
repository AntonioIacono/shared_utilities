#!/bin/bash

# Destination IP and Port
NEW_DESTINATION_IP="10.10.10.2"
NEW_DESTINATION_PORT="YOUR_DESTINATION_PORT"

# Define the port range
START_PORT=50000
END_PORT=51000

# Create port forwarding rules for each port in the range
for ((port = START_PORT; port <= END_PORT; port++)); do
    sudo iptables -t nat -i ens5 -A PREROUTING -p tcp --dport $port -j DNAT --to-destination $NEW_DESTINATION_IP:$port
    echo "$port"
   sudo iptables -t nat -A POSTROUTING -o ens5 -j SNAT --to-source "10.10.11.2"
done

# 