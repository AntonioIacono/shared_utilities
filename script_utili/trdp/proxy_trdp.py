import argparse
import threading
from scapy.all import sniff, sendp, Ether, IP, UDP

multicast_addresses = set()

def forward_packet(packet, forward_interface):
    sendp(packet, iface=forward_interface, verbose=0)

def packet_callback(packet):
    if IP in packet and UDP in packet:
        # Estraiamo informazioni dal pacchetto
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
        payload = bytes(packet[UDP].payload)

        # Effettuiamo l'analisi del payload se necessario
        # Qui puoi aggiungere la tua logica per l'analisi dei pacchetti fino al livello applicativo

        # Inoltriamo il pacchetto modificato
        forward_packet(packet, forward_interface)

def monitor_and_forward(interface, forward_interface):
    print(f"Monitoring and forwarding multicast UDP traffic from {interface} to {forward_interface}")
    
    sniff(iface=interface, prn=packet_callback, filter="udp and multicast", store=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor multicast traffic on a network interface and forward it to another physical interface')
    parser.add_argument('-i', '--interface', dest='interface', type=str, default='ens3', help='Network interface to monitor')
    parser.add_argument('-fi', '--forward_interface', dest='forward_interface', type=str, default='ens5', help='Network interface to forward traffic to')

    args = parser.parse_args()
    interface = args.interface
    forward_interface = args.forward_interface

    monitor_and_forward(interface, forward_interface)
