import socket
import struct
import time
import threading
import random
import tkinter as tk
from tkinter import ttk
import zlib
import uuid

# Definizione dei tipi di messaggio
msgTypes_values_PD = {
    "Pr": 20594,
    "Pp": 20592,
    "Pd": 20580,
    "Pe": 20581
}

msgTypes_values_MD = {
    "Mn": 19822,
    "Mr": 19826,
    "Mp": 19824,
    "Mq": 19825,
    "Mc": 19811,
    "Me": 19813
}

def calculate_crc(data):
    """Calculate CRC32 using the zlib library."""
    return zlib.crc32(data) & 0xFFFFFFFF

def createMessagePD(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip):
    while True:
        sequenceCounter += 1
        if lifeenabled:
            life += 1
            if life == 256:
                life = 0

        check = 1 if checkenabled else 0
        value1 = struct.pack('>I', sequenceCounter)
        value4 = struct.pack('>I', comId)
        value5 = struct.pack('>I', etbTopoCnt)
        value6 = struct.pack('>I', opTrnTopoCnt)
        value8 = struct.pack('>I', reserved01)
        value9 = struct.pack('>I', replyComId)
        
        ipSplit = replyIpAddress.split('.')
        array = [int(value) for value in ipSplit]
        value10 = struct.pack('B' * len(array), *array)
        
        value12 = struct.pack('B', life)
        value13 = struct.pack('B', check)

        # Convert binary string to bytes
        value14 = bytes(int(dataset[i:i+8], 2) for i in range(0, len(dataset), 8))
        value15 = value12 + value13 + value14
        value7 = struct.pack('>I', len(value15))

        # Construct the header without the CRC
        header_without_crc = value1 + struct.pack('<H', protocolVersion) + struct.pack('>H', msgType) + value4 + value5 + value6 + value7 + value8 + value9 + value10
        # Calculate the CRC over the header
        headerFcs = calculate_crc(header_without_crc)
        value11 = struct.pack('<I', headerFcs)

        # Complete header with CRC and payload
        payload = header_without_crc + value11 + value15
        send_udp_packet(ipAddress, port, payload, source_ip)
        time.sleep(timeValue / 1000)

def createMessageMD(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, replyStatus, sessionID, replyTimeout, sourceUri, destinationUri, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip):
    while True:
        sequenceCounter += 1
        if lifeenabled:
            life += 1
            if life == 256:
                life = 0

        check = 1 if checkenabled else 0

        # Pack the fixed fields
        value1 = struct.pack('>I', sequenceCounter)
        value2 = struct.pack('<H', protocolVersion)
        value3 = struct.pack('>H', msgType)
        value4 = struct.pack('>I', comId)
        value5 = struct.pack('>I', etbTopoCnt)
        value6 = struct.pack('>I', opTrnTopoCnt)
        value7 = struct.pack('>I', len(dataset))  # datasetLength
        value8 = struct.pack('>I', replyStatus)
        sessionId = uuid.uuid4()
        value9 = struct.pack('>IIII', sessionId)  # sessionId (4 UINT32s)
        value10 = struct.pack('>I', replyTimeout)
        value11 = sourceUri.ljust(32, '\x00').encode('ascii')  # sourceUri padded to 32 bytes
        value12 = destinationUri.ljust(32, '\x00').encode('ascii')  # destinationUri padded to 32 bytes

        value15 = struct.pack('B', life)
        value16 = struct.pack('B', check)
        
        # Pack the dataset (as a series of bytes)
        value13 = bytes(dataset)

        # Construct the header without the CRC
        header_without_crc = (value1 + value2 + value3 + value4 + value5 + value6 +
                              value7 + value8 + value9 + value10 + value11 + value12)
        
        # Calculate the CRC over the header
        headerFcs = calculate_crc(header_without_crc)
        value14 = struct.pack('<I', headerFcs)

        # Complete the message with CRC and dataset
        payload = header_without_crc + value14 + value15 + value16 + value13

        # Send the UDP packet
        send_udp_packet(ipAddress, port, payload, source_ip)

        # Wait before sending the next message
        time.sleep(timeValue / 1000)

def send_udp_packet(ip_address, port, payload, source_ip):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((source_ip, 0))
    # Set the TTL (Time-To-Live)
    ttl = struct.pack('B', 64)  # unsigned char as 1-byte object
    udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    try:
        # Send UDP packet
        udp_socket.sendto(payload, (ip_address, int(port)))
        print(f"Packet sent to {ip_address}:{port}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the socket
        udp_socket.close()

def start_thread_PD(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip):
    thread = threading.Thread(target=createMessagePD, args=(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip))
    thread.start()

def start_thread_MD(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip):
    thread = threading.Thread(target=createMessageMD, args=(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip))
    thread.start()

def create_dataset(dataset_length):
    num_bits = dataset_length * 8
    dataset = ''.join(random.choice('01') for _ in range(num_bits))
    return dataset

def show_selected_value(event):
    selected_type = msgType_combobox.get()
    associated_value = msgTypes_values_PD[selected_type]
    print(f"Tipo di Messaggio selezionato: {selected_type} - Valore associato: {associated_value}")

def reset_fields():
    ip_entry.delete(0, tk.END)
    port_entry.delete(0, tk.END)
    dataset_entry.delete(0, tk.END)
    sequence_cnt_entry.delete(0, tk.END)
    version_entry.delete(0, tk.END)
    msgType_combobox.set('')
    comid_entry.delete(0, tk.END)
    etbTopoCnt_entry.delete(0, tk.END)
    opTrnTopoCnt_entry.delete(0, tk.END)
    datasetLength_entry.delete(0, tk.END)
    reserved01_entry.delete(0, tk.END)
    replyComId_entry.delete(0, tk.END)
    replyIpAddress_entry.delete(0, tk.END)
    source_ip_entry.delete(0, tk.END)
    life_var.set(False)
    check_var.set(False)

def on_submit_PD():
    ip_destination = ip_entry.get()
    port = port_entry.get()
    dataset_life = int(dataset_entry.get())
    sequenceCounter = int(sequence_cnt_entry.get())
    protocolVersion = int(version_entry.get())
    msgType = msgTypes_values_PD[msgType_combobox.get()]
    comId = int(comid_entry.get())
    etbTopoCnt = int(etbTopoCnt_entry.get())
    opTrnTopoCnt = int(opTrnTopoCnt_entry.get())
    datasetLength = int(datasetLength_entry.get())
    reserved01 = int(reserved01_entry.get())
    replyComId = int(replyComId_entry.get())
    replyIpAddress = replyIpAddress_entry.get()
    headerFcs = 3572351821
    dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
    life_enabled = life_var.get()
    check_enabled = check_var.get()
    life = 0
    source_ip = source_ip_entry.get()

    start_thread_PD(ip_destination, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, life_enabled, check_enabled, life, source_ip)

    result = (
        f"ip_destination: {ip_destination}\n"
        f"port: {port}\n" 
        f"dataset_life: {dataset_life}\n"
        f"sequenceCounter: {sequenceCounter}\n"
        f"protocolVersion: {protocolVersion}\n"
        f"msgType: {msgType}\n"
        f"comId: {comId}\n"
        f"etbTopoCnt: {etbTopoCnt}\n"
        f"opTrnTopoCnt: {opTrnTopoCnt}\n"
        f"datasetLength: {datasetLength}\n"
        f"reserved01: {reserved01}\n"
        f"replyComId: {replyComId}\n"
        f"replyIpAddress: {replyIpAddress}\n"
        f"Life Abilitato: {'Sì' if life_enabled else 'No'}\n"
        f"Check Abilitato: {'Sì' if check_enabled else 'No'}\n"
        f"Life: {life}\n"
        f"Source IP: {source_ip}\n"
    )
    result_text_pd.insert(tk.END, result + "\n\n")
    # Reset fields after submission (optional)
    # reset_fields()



def on_submit_MD():
    ip_destination = ip_entry.get()
    port = port_entry.get()
    dataset_life = int(dataset_entry.get())
    sequenceCounter = int(sequence_cnt_entry.get())
    protocolVersion = int(version_entry.get())
    msgType = msgTypes_values_PD[msgType_combobox.get()]
    comId = int(comid_entry.get())
    etbTopoCnt = int(etbTopoCnt_entry.get())
    opTrnTopoCnt = int(opTrnTopoCnt_entry.get())
    datasetLength = int(datasetLength_entry.get())
    reserved01 = int(reserved01_entry.get())
    replyComId = int(replyComId_entry.get())
    replyIpAddress = replyIpAddress_entry.get()
    headerFcs = 3572351821
    dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
    life_enabled = life_var.get()
    check_enabled = check_var.get()
    life = 0
    source_ip = source_ip_entry.get()

    start_thread_MD(ip_destination, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, life_enabled, check_enabled, life, source_ip)

    result = (
        f"ip_destination: {ip_destination}\n"
        f"port: {port}\n" 
        f"dataset_life: {dataset_life}\n"
        f"sequenceCounter: {sequenceCounter}\n"
        f"protocolVersion: {protocolVersion}\n"
        f"msgType: {msgType}\n"
        f"comId: {comId}\n"
        f"etbTopoCnt: {etbTopoCnt}\n"
        f"opTrnTopoCnt: {opTrnTopoCnt}\n"
        f"datasetLength: {datasetLength}\n"
        f"reserved01: {reserved01}\n"
        f"replyComId: {replyComId}\n"
        f"replyIpAddress: {replyIpAddress}\n"
        f"Life Abilitato: {'Sì' if life_enabled else 'No'}\n"
        f"Check Abilitato: {'Sì' if check_enabled else 'No'}\n"
        f"Life: {life}\n"
        f"Source IP: {source_ip}\n"
    )
    result_text_md.insert(tk.END, result + "\n\n")
    # Reset fields after submission (optional)
    # reset_fields()


# Creazione della finestra principale
root = tk.Tk()
root.title("TRDP Generator")

# Creazione del frame principale per la griglia
main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

# Configurazione della griglia del main_frame
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.columnconfigure(2, weight=1)
main_frame.columnconfigure(3, weight=1)
main_frame.rowconfigure(0, weight=1)

# Creazione dei frame per i dati di input e risultati
framePD_input = tk.Frame(main_frame)
framePD_input.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

result_text_pd = tk.Text(main_frame, height=20, width=40)
result_text_pd.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

frameMD_input = tk.Frame(main_frame)
frameMD_input.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')

result_text_md = tk.Text(main_frame, height=20, width=40)
result_text_md.grid(row=0, column=3, padx=10, pady=10, sticky='nsew')



################
# PROCESS DATA #
################

# Titolo sopra i campi di input
tk.Label(framePD_input, text="Process Data", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='w')

# IP Destination
tk.Label(framePD_input, text="IP Destination:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
ip_entry = tk.Entry(framePD_input)
ip_entry.grid(row=1, column=1, padx=5, pady=5)

# Port
tk.Label(framePD_input, text="Port:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
port_entry = tk.Entry(framePD_input)
port_entry.grid(row=2, column=1, padx=5, pady=5)

# Dataset Life
tk.Label(framePD_input, text="Dataset Life:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
dataset_entry = tk.Entry(framePD_input)
dataset_entry.grid(row=3, column=1, padx=5, pady=5)

# Sequence Counter
tk.Label(framePD_input, text="Sequence Counter:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
sequence_cnt_entry = tk.Entry(framePD_input)
sequence_cnt_entry.grid(row=4, column=1, padx=5, pady=5)

# Protocol Version
tk.Label(framePD_input, text="Protocol Version:").grid(row=5, column=0, padx=5, pady=5, sticky='e')
version_entry = tk.Entry(framePD_input)
version_entry.grid(row=5, column=1, padx=5, pady=5)

# Message Type
tk.Label(framePD_input, text="Message Type:").grid(row=6, column=0, padx=5, pady=5, sticky='e')
msgType_combobox = ttk.Combobox(framePD_input, values=list(msgTypes_values_PD.keys()))
msgType_combobox.grid(row=6, column=1, padx=5, pady=5)
msgType_combobox.bind("<<ComboboxSelected>>", show_selected_value)

# ComID
tk.Label(framePD_input, text="ComID:").grid(row=7, column=0, padx=5, pady=5, sticky='e')
comid_entry = tk.Entry(framePD_input)
comid_entry.grid(row=7, column=1, padx=5, pady=5)

# ETB Topo Cnt
tk.Label(framePD_input, text="ETB Topo Cnt:").grid(row=8, column=0, padx=5, pady=5, sticky='e')
etbTopoCnt_entry = tk.Entry(framePD_input)
etbTopoCnt_entry.grid(row=8, column=1, padx=5, pady=5)

# OP Trn Topo Cnt
tk.Label(framePD_input, text="OP Trn Topo Cnt:").grid(row=9, column=0, padx=5, pady=5, sticky='e')
opTrnTopoCnt_entry = tk.Entry(framePD_input)
opTrnTopoCnt_entry.grid(row=9, column=1, padx=5, pady=5)

# Dataset Length
tk.Label(framePD_input, text="Dataset Length:").grid(row=10, column=0, padx=5, pady=5, sticky='e')
datasetLength_entry = tk.Entry(framePD_input)
datasetLength_entry.grid(row=10, column=1, padx=5, pady=5)

# Reserved01
tk.Label(framePD_input, text="Reserved01:").grid(row=11, column=0, padx=5, pady=5, sticky='e')
reserved01_entry = tk.Entry(framePD_input)
reserved01_entry.grid(row=11, column=1, padx=5, pady=5)

# Reply ComID
tk.Label(framePD_input, text="Reply ComID:").grid(row=12, column=0, padx=5, pady=5, sticky='e')
replyComId_entry = tk.Entry(framePD_input)
replyComId_entry.grid(row=12, column=1, padx=5, pady=5)

# Reply IP Address
tk.Label(framePD_input, text="Reply IP Address:").grid(row=13, column=0, padx=5, pady=5, sticky='e')
replyIpAddress_entry = tk.Entry(framePD_input)
replyIpAddress_entry.grid(row=13, column=1, padx=5, pady=5)

# Source IP
tk.Label(framePD_input, text="Source IP:").grid(row=14, column=0, padx=5, pady=5, sticky='e')
source_ip_entry = tk.Entry(framePD_input)
source_ip_entry.grid(row=14, column=1, padx=5, pady=5)

# Life Enabled
life_var = tk.BooleanVar()
life_checkbox = tk.Checkbutton(framePD_input, text="Life Enabled", variable=life_var)
life_checkbox.grid(row=15, columnspan=2, pady=5)

# Check Enabled
check_var = tk.BooleanVar()
check_checkbox = tk.Checkbutton(framePD_input, text="Check Enabled", variable=check_var)
check_checkbox.grid(row=16, columnspan=2, pady=5)

# Submit Button
submit_button = tk.Button(framePD_input, text="Invia", command=on_submit_PD)
submit_button.grid(row=17, columnspan=2, pady=10)

# Result Text
result_text_pd = tk.Text(main_frame, height=20, width=40)
result_text_pd.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')



################
# MESSAGE DATA #
################

# Titolo sopra i campi di input
tk.Label(frameMD_input, text="Message Data", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky='w')

# IP Destination
tk.Label(frameMD_input, text="IP Destination:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
ip_entry = tk.Entry(frameMD_input)
ip_entry.grid(row=1, column=1, padx=5, pady=5)

# Port
tk.Label(frameMD_input, text="Port:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
port_entry = tk.Entry(frameMD_input)
port_entry.grid(row=2, column=1, padx=5, pady=5)

# Dataset Life
tk.Label(frameMD_input, text="Dataset Life:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
dataset_entry = tk.Entry(frameMD_input)
dataset_entry.grid(row=3, column=1, padx=5, pady=5)

# Sequence Counter
tk.Label(frameMD_input, text="Sequence Counter:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
sequence_cnt_entry = tk.Entry(frameMD_input)
sequence_cnt_entry.grid(row=4, column=1, padx=5, pady=5)

# Protocol Version
tk.Label(frameMD_input, text="Protocol Version:").grid(row=5, column=0, padx=5, pady=5, sticky='e')
version_entry = tk.Entry(frameMD_input)
version_entry.grid(row=5, column=1, padx=5, pady=5)

# Message Type
tk.Label(frameMD_input, text="Message Type:").grid(row=6, column=0, padx=5, pady=5, sticky='e')
msgType_combobox = ttk.Combobox(frameMD_input, values=list(msgTypes_values_PD.keys()))
msgType_combobox.grid(row=6, column=1, padx=5, pady=5)
msgType_combobox.bind("<<ComboboxSelected>>", show_selected_value)

# ComID
tk.Label(frameMD_input, text="ComID:").grid(row=7, column=0, padx=5, pady=5, sticky='e')
comid_entry = tk.Entry(frameMD_input)
comid_entry.grid(row=7, column=1, padx=5, pady=5)

# ETB Topo Cnt
tk.Label(frameMD_input, text="ETB Topo Cnt:").grid(row=8, column=0, padx=5, pady=5, sticky='e')
etbTopoCnt_entry = tk.Entry(frameMD_input)
etbTopoCnt_entry.grid(row=8, column=1, padx=5, pady=5)

# OP Trn Topo Cnt
tk.Label(frameMD_input, text="OP Trn Topo Cnt:").grid(row=9, column=0, padx=5, pady=5, sticky='e')
opTrnTopoCnt_entry = tk.Entry(frameMD_input)
opTrnTopoCnt_entry.grid(row=9, column=1, padx=5, pady=5)

# Dataset Length
tk.Label(frameMD_input, text="Dataset Length:").grid(row=10, column=0, padx=5, pady=5, sticky='e')
datasetLength_entry = tk.Entry(frameMD_input)
datasetLength_entry.grid(row=10, column=1, padx=5, pady=5)

# Reserved01
tk.Label(frameMD_input, text="Reserved01:").grid(row=11, column=0, padx=5, pady=5, sticky='e')
reserved01_entry = tk.Entry(frameMD_input)
reserved01_entry.grid(row=11, column=1, padx=5, pady=5)

# Reply ComID
tk.Label(frameMD_input, text="Reply ComID:").grid(row=12, column=0, padx=5, pady=5, sticky='e')
replyComId_entry = tk.Entry(frameMD_input)
replyComId_entry.grid(row=12, column=1, padx=5, pady=5)

# Reply IP Address
tk.Label(frameMD_input, text="Reply IP Address:").grid(row=13, column=0, padx=5, pady=5, sticky='e')
replyIpAddress_entry = tk.Entry(frameMD_input)
replyIpAddress_entry.grid(row=13, column=1, padx=5, pady=5)

# Source IP
tk.Label(frameMD_input, text="Source IP:").grid(row=14, column=0, padx=5, pady=5, sticky='e')
source_ip_entry = tk.Entry(frameMD_input)
source_ip_entry.grid(row=14, column=1, padx=5, pady=5)

# Life Enabled
life_var = tk.BooleanVar()
life_checkbox = tk.Checkbutton(frameMD_input, text="Life Enabled", variable=life_var)
life_checkbox.grid(row=15, columnspan=2, pady=5)

# Check Enabled
check_var = tk.BooleanVar()
check_checkbox = tk.Checkbutton(frameMD_input, text="Check Enabled", variable=check_var)
check_checkbox.grid(row=16, columnspan=2, pady=5)

# Submit Button
submit_button = tk.Button(frameMD_input, text="Invia", command=on_submit_MD)
submit_button.grid(row=17, columnspan=2, pady=10)

# Result Text
result_text_pd = tk.Text(main_frame, height=20, width=40)
result_text_pd.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')


# Start the main loop
root.mainloop()
