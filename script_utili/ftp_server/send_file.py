from ftplib import FTP
import os

def upload_file(ftp, local_file_path, remote_file_name):
    try:
        with open(local_file_path, 'rb') as file:
            ftp.storbinary(f'STOR {remote_file_name}', file)
        print(f"File '{local_file_path}' uploaded successfully as '{remote_file_name}'.")
    except FileNotFoundError:
        print(f"Error: Local file '{local_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred during file upload: {str(e)}")

if __name__ == "__main__":
    # FTP server details
    ftp_host = 'ftp.example.com'
    ftp_port = 21
    username = 'your_username'
    password = 'your_password'
    target_directory = '/upload'  # Change this to your target directory

    # Local file to upload
    local_file_path = 'path/to/your/local/file.txt'
    remote_file_name = os.path.basename(local_file_path)  # Use the local file name for remote file name

    try:
        # Connect to the FTP server
        ftp = FTP()
        ftp.connect(ftp_host, ftp_port)
        ftp.login(username, password)

        # Change to the target directory (if not root)
        if target_directory:
            ftp.cwd(target_directory)

        # Upload the file
        upload_file(ftp, local_file_path, remote_file_name)

        # Close FTP connection
        ftp.quit()
        print("FTP session closed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
