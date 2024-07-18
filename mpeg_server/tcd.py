import threading
import subprocess

# Comando per ricevere il primo flusso
command1 = [
    "ffmpeg",
    "-i", "http://172.23.0.190:8080/stream/video-15mbs.mkv",
    "-localaddr", "172.16.1.200",  # Sostituisci con l'indirizzo IP della tua NIC
    "-f", "null",
    "-",
    "-stats"
]

# Comando per ricevere il secondo flusso
command2 = [
    "ffmpeg",
    "-i", "http://172.23.0.190:8080/stream/video-15mbs.mkv",
    "-localaddr", "172.16.2.200",  # Sostituisci con l'indirizzo IP della tua NIC
    "-f", "null",
    "-",
    "-stats"
]

# Funzione che esegue il comando ffmpeg
def run_ffmpeg(ffmpeg_command):
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di ffmpeg: {e}")

# Creazione e avvio del primo thread
ffmpeg_thread1 = threading.Thread(target=run_ffmpeg, args=(command1,))
ffmpeg_thread1.start()

# Creazione e avvio del secondo thread
ffmpeg_thread2 = threading.Thread(target=run_ffmpeg, args=(command2,))
ffmpeg_thread2.start()
