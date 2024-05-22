#!/bin/sh
#Set up the paths(relatives paths)
ground_notify_msg="./ground_notify_message.py"
vsftpd_log="/var/log/vsftpd.log"
xmpp_bot="./bot.py"

#Set up cycle time



#Start
python3 "$xmpp_bot" &

#clear log
> "$vsftpd_log"

#Monitor the log file for new entries
tail -F $vsftpd_log | while read line;do
	if echo "$line" | grep -q 'ftp';then
		echo "File uploaded";
                python3 $ground_notify_msg
	fi
done
