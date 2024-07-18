import threading
import subprocess
import socket

# Function that sets up the socket to bind to a specific interface
def create_bound_socket(interface_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((interface_ip, 0))
    return s

# Command for receiving the stream
command = [
    "ffmpeg",
    "-i", "http://172.23.0.190:8080/stream/video-15mbs.mkv",
    "-f", "null",
    "-",
    "-stats"
]

# Function that executes the ffmpeg command
def run_ffmpeg(ffmpeg_command, interface_ip):
    s = create_bound_socket(interface_ip)
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di ffmpeg: {e}")
    finally:
        s.close()

# IP addresses of the interfaces
interface_ip1 = "172.16.1.200"  # Replace with the IP address of your NIC
interface_ip2 = "172.16.2.200"  # Replace with the IP address of your NIC

# Creating and starting the first thread
ffmpeg_thread1 = threading.Thread(target=run_ffmpeg, args=(command, interface_ip1))
ffmpeg_thread1.start()

# Creating and starting the second thread
ffmpeg_thread2 = threading.Thread(target=run_ffmpeg, args=(command, interface_ip2))
ffmpeg_thread2.start()

# Wait for both threads to finish (optional)
ffmpeg_thread1.join()
ffmpeg_thread2.join()

print("I comandi ffmpeg sono stati lanciati in thread separati.")
