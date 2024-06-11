import argparse
import threading
from scapy.all import sniff, sendp, Ether
from queue import Queue

def forward_packet(packet, forward_interface):
    sendp(packet, iface=forward_interface, verbose=0)

def packet_worker(q, forward_interface):
    while True:
        packet = q.get()
        forward_packet(packet, forward_interface)
        q.task_done()

def monitor_and_forward(interface, forward_interface):
    print(f"Monitoring and forwarding multicast UDP traffic from {interface} to {forward_interface}")
    
    # Aumentiamo la dimensione della coda
    packet_queue = Queue(maxsize=10000000)  # Possiamo regolare la dimensione della coda a seconda delle esigenze

    # Avvio i thread lavoratori
    for _ in range(4):  # Possiamo regolare il numero di thread a seconda delle esigenze
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