import socket
import struct
import argparse
import threading
from scapy.all import sniff, sendp, Ether, IP, UDP

# Set of multicast addresses to filter
multicast_addresses = {"239.18.1.1", "239.18.1.10", "239.13.1.1", "239.13.1.10"}
detected_multicast_addresses = set()

def forward_packet(data, forward_interface, src_ip, dst_ip, dst_port):
    # Build the Ethernet packet
    ether = Ether()
    
    # Build the IP packet
    ip = IP(src=src_ip, dst=dst_ip)
    
    # Build the UDP packet
    udp = UDP(dport=dst_port, sport=dst_port)
    
    # Send the packet
    packet = ether / ip / udp / data
    sendp(packet, iface=forward_interface, verbose=0)

def listen_udp_multicast(multicast_ip, port, listen_ip, forward_interface, source_ip_forward):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind((listen_ip, port))

    # Join multicast group
    mreq = struct.pack('4s4s', socket.inet_aton(multicast_ip), socket.inet_aton(listen_ip))
    udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Listening on {multicast_ip}:{port} via {listen_ip}")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        print(f"Received packet from {addr} on {multicast_ip}")

        # Directly forward the packet
        forward_packet(data, forward_interface, source_ip_forward, multicast_ip, port)

def start_listening_thread(multicast_ip, port, listen_ip, forward_interface, source_ip_forward):
    thread = threading.Thread(target=listen_udp_multicast, args=(multicast_ip, port, listen_ip, forward_interface, source_ip_forward))
    thread.start()
    return thread

def packet_callback(packet):
    if IP in packet and packet[IP].dst.startswith("239."):
        multicast_ip = packet[IP].dst
        if multicast_ip not in detected_multicast_addresses:
            detected_multicast_addresses.add(multicast_ip)
            print(f"New multicast address detected: {multicast_ip}")
            start_listening_thread(multicast_ip, port, listen_ip, forward_interface, source_ip_forward)

def monitor_multicast_traffic(interface, port, listen_ip, forward_interface, source_ip_forward):
    print(f"Starting multicast traffic monitoring on interface: {interface}")
    
    # Start threads for predefined multicast addresses
    for multicast_ip in multicast_addresses:
        start_listening_thread(multicast_ip, port, listen_ip, forward_interface, source_ip_forward)
    
    # Monitor for new multicast addresses
    sniff(iface=interface, prn=packet_callback, filter="ip multicast", store=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor multicast traffic on a network interface and forward it to another physical interface')
    parser.add_argument('-i', '--interface', dest='interface', type=str, default='ens3', help='Network interface to monitor')
    parser.add_argument('-p', '--port', dest='port', type=int, default=17224, help='Port to listen on')
    parser.add_argument('-l', '--listen', dest='listen_ip', type=str, default='0.0.0.0', help='Local IP address to listen on')
    parser.add_argument('-fi', '--forward_interface', dest='forward_interface', type=str, default='ens5', help='Network interface to forward traffic to')
    parser.add_argument('-fs', '--source_ip_forward', dest='source_ip_forward', type=str, default='172.23.0.13', help='IP address to forward traffic from')

    args = parser.parse_args()
    interface = args.interface
    port = args.port
    listen_ip = args.listen_ip
    forward_interface = args.forward_interface
    source_ip_forward = args.source_ip_forward

    monitor_multicast_traffic(interface, port, listen_ip, forward_interface, source_ip_forward)
