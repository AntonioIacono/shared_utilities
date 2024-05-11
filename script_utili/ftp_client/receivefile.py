from ftplib import FTP
import socket
import threading


def retr_file():
    print("1")
    ftp.set_pasv(False)
    command= ''.join(['RETR ', file_name])
    response = ftp.sendcmd(command)  # Replace>
    print(response)
    print("concluso file")

def data_connection():
    print("2")
    conn, addr = data_socket.accept()
    print(f"Connection from: {addr}")

    # Receive data
    data = conn.recv(1024)
    print(f"Received data: {data.decode()}")
    with open('test.txt', 'wb') as local_file:
        local_file.write(data)
    # Close the connection
    conn.close()
    data_socket.close()
    print("concluso data")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 receivefile.py file_to_receive.txt")
        exit(0)
    else:
        file_name = sys.argv[1]
        
    # FTP server details
    ftp_host = '10.10.11.2'
    ftp_port = 21
    data_port = 25600  # The data channel port you want to use
    username = 'admin'
    password = '123'
    # Set up the socket
    data_port = 25600
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    data_socket.bind(('10.10.10.2', data_port))
    data_socket.listen(1) 
    try:
        # Connect to the FTP server
        ftp = FTP()
        ftp.connect(ftp_host, ftp_port)
    
        # Login with credentials
        ftp.login(username, password)
    
        # Send a PORT command to specify the data channel port
        data_host = '10.10.10.2'  # Replace with the appropriate data channel IP
        port_command = 'PORT {},{},{}'.format(','.join(data_host.split('.')), data_port // 256, data_port % 256)
        print(port_command)
        thread_receive_data = threading.Thread(target=data_connection)
    
        thread_retr_file = threading.Thread(target=retr_file)
    
        thread_receive_data.start()
        thread_retr_file.start()
        print("Lanciati")

        thread_receive_data.join()
        thread_retr_file.join()
        print("File ricevuto correttamente")


        ftp.quit()
        print(f"Terminato")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


