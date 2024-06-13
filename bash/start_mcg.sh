#!/bin/bash

# Set up the paths (relatives)
send_file_ftp="./../ftp/send_file.py"
file_to_send="./../ftp/test.txt"
xmpp_bot="./../xmpp/bot.py"
xmpp_presence="./../xmpp/presence.py"

# Set timer
ftp_time=2 # every 2 seconds
presence_time=3 # every 3 seconds

# Define functions

function start_bot {
    python3 "$xmpp_bot" -j mcg@xmpp-server.sw1.multimedia.arpa -p password -t mcu@xmpp-server.sw1.multimedia.arpa &
}

function send_file {
    echo "FTP Sending"
    python3 "$send_file_ftp"
    sleep $ftp_time 
}

function send_presence_msg {
    python3 "$xmpp_presence" -j mcg@xmpp-server.sw1.multimedia.arpa -p password -t mcu@xmpp-server.sw1.multimedia.arpa  
}

# START

start_bot &

while true; do
    send_file &
    send_presence_msg &
    wait
done
