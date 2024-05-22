#!/bin/sh

tail -F /var/log/vsftpd.log | while read line;do
	if echo "$line" | grep -q 'ftp';then
		echo "File uploaded";
                /bin/python3 xmpp-mcu/ground_notify_message.py
	fi
done
