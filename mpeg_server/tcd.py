import subprocess

# Comando per ricevere il primo flusso
command1 = [
    'ffmpeg',
    '-i', 'http://172.23.0.190/stream/video.mpeg',
    '-f', 'null', '-'
]

# Comando per ricevere il secondo flusso
command2 = [
    'ffmpeg',
    '-i', 'http://172.23.0.190/stream/video.mpeg',
    '-f', 'null', '-'
]

# Avvia due processi ffmpeg
process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Attendere che entrambi i processi abbiano completato
stdout1, stderr1 = process1.communicate()
stdout2, stderr2 = process2.communicate()

# Gestire eventuali output o errori, se necessario
print("Process 1 STDOUT:", stdout1.decode())
print("Process 1 STDERR:", stderr1.decode())
print("Process 2 STDOUT:", stdout2.decode())
print("Process 2 STDERR:", stderr2.decode())
