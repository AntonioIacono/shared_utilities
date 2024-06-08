import argparse
import threading
import struct
from scapy.all import sniff, sendp, Ether, IP, UDP, Raw
from queue import Queue

def parse_trdp_packet(data):
    sequenceCounter = struct.unpack('>I', data[0:4])[0]
    protocolVersion, msgType = struct.unpack('>HH', data[4:8])
    comId = struct.unpack('>I', data[8:12])[0]
    etbTopoCnt = struct.unpack('>I', data[12:16])[0]
    opTrnTopoCnt = struct.unpack('>I', data[16:20])[0]
    datasetLength = struct.unpack('>I', data[20:24])[0]
    reserved01 = struct.unpack('>I', data[24:28])[0]
    replyComId = struct.unpack('>I', data[28:32])[0]
    replyIpAddress = '.'.join(map(str, data[32:36]))
    headerFcs = struct.unpack('>I', data[36:40])[0]
    life = data[40]
    check = data[41]
    dataset = ''.join(f'{byte:08b}' for byte in data[42:])

    return {
        'sequenceCounter': sequenceCounter,
        'protocolVersion': protocolVersion,
        'msgType': msgType,
        'comId': comId,
        'etbTopoCnt': etbTopoCnt,
        'opTrnTopoCnt': opTrnTopoCnt,
        'datasetLength': datasetLength,
        'reserved01': reserved01,
        'replyComId': replyComId,
        'replyIpAddress': replyIpAddress,
        'headerFcs': headerFcs,
        'life': life,
        'check': check,
        'dataset': dataset
    }

def forward_packet(packet, forward_interface):
    sendp(packet, iface=forward_interface, verbose=0)

def packet_worker(q, forward_interface):
    while True:
        packet = q.get()

        # Controlla se il pacchetto ha un payload Raw
        if Raw in packet:
            data = bytes(packet[Raw])
        # Effettua il parsing del pacchetto
            parsed_packet = parse_trdp_packet(data)
            #print(parsed_packet)
            if parsed_packet['comId'] == 40003:
                forward_packet(packet, forward_interface)
        q.task_done()

def monitor_and_forward(interface, forward_interface):
    print(f"Monitoring and forwarding multicast UDP traffic from {interface} to {forward_interface}")
    
    # Aumentiamo la dimensione della coda
    packet_queue = Queue(maxsize=1000)  # Possiamo regolare la dimensione della coda a seconda delle esigenze

    # Avvio i thread lavoratori
    for _ in range(100):  # Possiamo regolare il numero di thread a seconda delle esigenze
        t = threading.Thread(target=packet_worker, args=(packet_queue, forward_interface), daemon=True)
        t.start()

    # Callback per sniffing e invio dei pacchetti alla coda
    sniff(iface=interface, prn=lambda x: packet_queue.put(x), filter="udp and multicast", store=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple script to sniff and forward UDP multicast traffic from one interface to another')
    parser.add_argument('-i', '--interface', dest='interface', type=str, default='ens3', help='Source network interface to sniff multicast UDP traffic from')
    parser.add_argument('-fi', '--forward_interface', dest='forward_interface', type=str, default='ens5', help='Network interface to forward traffic to')

    args = parser.parse_args()
    interface = args.interface
    forward_interface = args.forward_interface

    monitor_and_forward(interface, forward_interface)
