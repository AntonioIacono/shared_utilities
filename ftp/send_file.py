from ftplib import FTP
import socket
import time

def data_connection():
    conn, addr = data_socket.accept()
    print(f"Connection from: {addr}")

    # Receive data
    data = conn.recv(1024)
    print(f"Received data: {data.decode()}")
    # Close the connection
    conn.close()
    data_socket.close()


# FTP server details
ftp_host = '172.23.0.118'
ftp_port = 21
data_port = 25600  # The data channel port you want to use
username = 'admin'
password = '123'
# Set up the socket
data_port = 25600
data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
data_socket.bind(('172.16.1.150', data_port))
data_socket.listen(1)
try:
    # Connect to the FTP server
    ftp = FTP()
    ftp.connect(ftp_host, ftp_port)
    
    # Login with credentials
    ftp.login(username, password)
    
    # Send a PORT command to specify the data channel port
    data_host = '172.16.1.150'  # Replace with the appropriate data channel IP
    port_command = 'PORT {},{},{}'.format(','.join(data_host.split('.')), data_port // 256, data_port % 256)
    print(port_command)
    response = ftp.sendcmd(port_command)
    print(response)

    # Execute the LIST command
    #response = ftp.sendcmd('LIST')
    #print(response)

    #data_connection()
    #response = ftp.sendcmd('MKD')
    local_file_path = './../ftp/test.txt'
    remote_file_path = './../ftp/test.txt' 
    ftp.set_pasv(False)
   
   with open(local_file_path, 'rb') as file:
            ftp.storbinary(f'STOR {remote_file_path}',file)
    
    ftp.close()
    print(f"Terminato")

except Exception as e:
    print(f"An error occurred: {str(e)}")
