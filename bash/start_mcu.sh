#!/bin/bash

#Set up the paths (relatives)
vsftpd_log="/var/log/vsftpd.log"
xmpp_bot="./../xmpp/bot.py"
xmpp_notify="./../xmpp/ground_notify_message.py"

#Set timer
ftp_time=2 # every 2 seconds
presence_time=3 #every 3 seconds


#Define functions
function start_bot {
    python3 "$xmpp_bot" -j mcu@xmpp-server.sw1.multimedia.arpa -p password  &
}


function send_notify_msg {
    python3 "$xmpp_presence" -j mcu@xmpp-server.sw1.multimedia.arpa -p password -t mcg@xmpp-server.sw1.multimedia.arpa  
}


#START

start_bot &

#clear log
>"$vsftpd_log"

#Monitor the log file for new entries

tail -F $vsftpd_log | while read line;do
        if echo "$line" | grep -q 'ftp'; then
            echo "File Uploaded";
            send_notify_msg
        fi
done