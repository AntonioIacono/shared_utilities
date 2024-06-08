import argparse
import threading
from scapy.all import sniff, sendp, Ether

def forward_packet(packet, forward_interface):
    sendp(packet, iface=forward_interface, verbose=0)

def monitor_and_forward(interface, forward_interface):
    print(f"Monitoring and forwarding multicast UDP traffic from {interface} to {forward_interface}")
    
    def packet_callback(packet):
        forward_packet(packet, forward_interface)

    sniff(iface=interface, prn=packet_callback, filter="udp and multicast", store=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple script to sniff and forward UDP multicast traffic from one interface to another')
    parser.add_argument('-i', '--interface', dest='interface', type=str, default='ens3', help='Source network interface to sniff multicast UDP traffic from')
    parser.add_argument('-fi', '--forward_interface', dest='forward_interface', type=str, default='ens5', help='Network interface to forward traffic to')

    args = parser.parse_args()
    interface = args.interface
    forward_interface = args.forward_interface

    monitor_and_forward(interface, forward_interface)
