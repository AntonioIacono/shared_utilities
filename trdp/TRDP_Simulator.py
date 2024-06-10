import socket
import struct
import time
import tkinter as tk
from tkinter import ttk



def createMessage(ipAddress,port,timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset,lifeenabled, checkenabled, life):
    while True:
        sequenceCounter = sequenceCounter + 1
        life = life + 1 if lifeenabled else 1
        if life == 256:
            life = 0

        check = 1 if checkenabled else 0
        value1 = struct.pack('>I',sequenceCounter)

        value4 = struct.pack('>I',comId)
        value5 = struct.pack('>I',etbTopoCnt)
        value6 = struct.pack('>I',opTrnTopoCnt)
    
        value8 = struct.pack('>I',reserved01)
        value9 = struct.pack('>I',replyComId)
        ipSplit = replyIpAddress.split('.')
        i = 0
        array = []
        for value in ipSplit:
            
            array.append(int(value))
        values_to_pack = [valore for valore in array]
        print(array)
        value10 = struct.pack('B'* len(array), *array)
            
        value11 = struct.pack('>I',headerFcs)
        mettiInsieme = struct.pack('HH', protocolVersion, msgType)
        while len(dataset) % 8 != 0:
            dataset += '0'
        value12 = struct.pack('B', life)
        value13 = struct.pack('B', check)

        # Convert binary string to bytes
        value14 = bytes(int(dataset[i:i+8], 2) for i in range(0, len(dataset), 8))
        value15 = value12 + value13 + value14
        value7 = struct.pack('>I',len(value15))

        payload = value1+mettiInsieme+value4+value5+value6+value7+value8+value9+value10+value11+value15
        send_udp_packet(ipAddress, port, payload, time)
        time.sleep(timeValue/1004)


def send_udp_packet(ip_address, port, payload, time_value):

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Invio del pacchetto UDP
        udp_socket.sendto(payload, (ip_address, port))
        print(f"Pacchetto inviato a {ip_address}:{port}")
    except Exception as e:
        print(f"Errore durante l'invio del pacchetto: {e}")
    finally:
        # Chiusura del socket
        udp_socket.close()


    
def on_submit():
    ip_multicast = ip_entry.get()
    comid = comid_entry.get()
    dataset_life = dataset_entry.get()
    life_enabled = life_var.get()
    check = check_var.get()
    dataset_type = dataset_type_combobox.get()
    port = 17224

    createMessage(str(ip_multicast),port,int(dataset_life),4035626,1,29264,int(comid),0,0,4,0,int(comid),str(ip_multicast),3572351821,"00000000000000000000000000000001111111111111111111111111101111111110101010110101101010101011111",life_enabled,check,0)

    result = (
        f"IP Multicast: {ip_multicast}\n"
        f"Dataset Life: {dataset_life}\n"
        f"Dataset Type: {dataset_type}\n"
        f"Life Abilitato: {'Sì' if life_enabled else 'No'}"
    )
    result_label.config(text=result)

# Creazione della finestra principale
root = tk.Tk()
root.title("Configurazione Multicast")

# Creazione del frame principale
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Creazione dell'etichetta e del campo di inserimento per l'IP Multicast
tk.Label(frame, text="Inserisci IP Multicast:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
ip_entry = tk.Entry(frame)
ip_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Inserisci ComID:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
comid_entry = tk.Entry(frame)
comid_entry.grid(row=1, column=1, padx=5, pady=5)

# Creazione dell'etichetta e del campo di inserimento per il dataset life
tk.Label(frame, text="Dataset Life:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
dataset_entry = tk.Entry(frame)
dataset_entry.grid(row=2, column=1, padx=5, pady=5)

# Creazione dell'etichetta e del combobox per il tipo di dataset
tk.Label(frame, text="Tipo di Dataset:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
dataset_type_combobox = ttk.Combobox(frame, values=["mcg", "mdcu", "pis"])
dataset_type_combobox.grid(row=3, column=1, padx=5, pady=5)
dataset_type_combobox.current(0)  # Imposta l'elemento predefinito

# Creazione del checkbox per abilitare o disabilitare life
life_var = tk.BooleanVar()
life_checkbox = tk.Checkbutton(frame, text="Life Abilitato", variable=life_var)
life_checkbox.grid(row=4, columnspan=2, pady=5)

# Creazione del checkbox per abilitare o disabilitare life
check_var = tk.BooleanVar()
check_checkbox = tk.Checkbutton(frame, text="Check Abilitato", variable=check_var)
check_checkbox.grid(row=5, columnspan=2, pady=5)


# Creazione del pulsante di invio
submit_button = tk.Button(frame, text="Invia", command=on_submit)
submit_button.grid(row=6, columnspan=2, pady=10)

# Creazione dell'etichetta per mostrare i risultati
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

# Avvio del ciclo principale della GUI
root.mainloop()