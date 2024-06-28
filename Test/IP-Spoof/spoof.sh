#!/bin/bash

# Define the range of IP addresses
START_IP=172.23.0.1
END_IP=172.23.0.255
TARGET_IP=172.23.0.2
PORT=80

# Function to convert IP to integer
ip_to_int(){
    local a b c d
    IFS=. read -r a b c d <<< "$1"
    echo "$((a << 24 | b << 16 | c << 8 | d))"
}

# Function to convert integer to IP
int_to_ip() {
    local num=$1
    echo "$(( (num >> 24) & 255 )).$(( (num >> 16) & 255 )).$(( (num >> 8) & 255 )).$(( num & 255 ))"
}

# Convert start and end IPs to integers
start_int=$(ip_to_int $START_IP)
end_int=$(ip_to_int $END_IP)

# Loop through the range
for ((i=start_int; i<=end_int; i++)); do
    spoofed_ip=$(int_to_ip $i)
    echo "Spoofing IP: $spoofed_ip"
    nmap -S $spoofed_ip -p $PORT $TARGET_IP
done
