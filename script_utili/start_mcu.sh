#!/bin/sh
#Set up the paths(relatives paths)
ground_notify_msg="./xmpp/ground_notify_message.py"
vsftpd_log="/var/log/vsftpd.log"
xmpp_bot="./xmpp/bot.py"

#Set up cycle time



#Start
python3 "$xmpp_bot" &

tail -F $vsftpd_log | while read line;do
	if echo "$line" | grep -q 'ftp';then
		echo "File uploaded";
                /bin/python3 xmpp-mcu/ground_notify_message.py
	fi
done
