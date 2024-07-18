import threading
import subprocess
import socket
import fcntl
import struct

# Function that sets up the socket to bind to a specific interface
def create_bound_socket(interface_name):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ifname = interface_name.encode('utf-8')
    fcntl.ioctl(s, 0x8933, struct.pack('256s', ifname[:15]))
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
def run_ffmpeg(ffmpeg_command, interface_name):
    s = create_bound_socket(interface_name)
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di ffmpeg: {e}")
    finally:
        s.close()

# Names of the interfaces
interface_name1 = "ens3"  # Replace with the name of your network interface
interface_name2 = "ens4"  # Replace with the name of your network interface

# Creating and starting the first thread
ffmpeg_thread1 = threading.Thread(target=run_ffmpeg, args=(command, interface_name1))
ffmpeg_thread1.start()

# Creating and starting the second thread
ffmpeg_thread2 = threading.Thread(target=run_ffmpeg, args=(command, interface_name2))
ffmpeg_thread2.start()

# Wait for both threads to finish (optional)
ffmpeg_thread1.join()
ffmpeg_thread2.join()

print("I comandi ffmpeg sono stati lanciati in thread separati.")
