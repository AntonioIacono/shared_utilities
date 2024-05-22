#!/bin/bash

#Set up the paths for the scripts
#This are relative paths
script_ftp="./send_file.py"
script_xmpp_bot="./bot.py"
script_xmpp_presence="./presence.py"


#Set Up cycle time
ftp_time=2 #2 seconds
presence_time=3 #3 seconds

#Define functions

function start_bot {
    python3 "$script_xmpp_bot" &
}

function ftp_send {
    echo "FTP Sending";
    python3 "$script_ftp"
    sleep $ftp_time
}


function presence_msg {
    echo "XMPP Presence Sending";
    python3 "$script_xmpp_presence"
    sleep $presence_time
}


#START
start_bot &

while true; do

    ftp_send & 
#    presence_msg & 
    wait
done
