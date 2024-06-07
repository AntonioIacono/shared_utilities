import socket
import struct
import argparse
import threading
from scapy.all import sniff, sendp, Ether, IP, UDP, conf

multicast_addresses = set()

def parse_trdp_packet(data):
    # Extract fields from TRDP packets
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

def forward_packet(data, forward_interface, src_mac, dst_mac, src_ip, dst_ip, dst_port):
    # Costruisci il pacchetto Ethernet
    ether = Ether(src=src_mac, dst=dst_mac)
    
    # Costruisci il pacchetto IP
    ip = IP(src=src_ip, dst=dst_ip)
    
    # Costruisci il pacchetto UDP
    udp = UDP(sport=dst_port, dport=dst_port)
    
    # Invia il pacchetto
    packet = ether / ip / udp / data
    sendp(packet, iface=forward_interface)

def listen_udp_multicast(multicast_ip, port, listen_ip, forward_interface, src_mac, dst_mac, dst_port):
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

        parsed_packet = parse_trdp_packet(data)
        for key, value in parsed_packet.items():
            print(f"{key}: {value}")

        forward_packet(data, forward_interface, src_mac, dst_mac, listen_ip, multicast_ip, dst_port)

def packet_callback(packet):
    if IP in packet and (packet[IP].dst.startswith("224.") or packet[IP].dst.startswith("239.")):
        multicast_ip = packet[IP].dst
        if multicast_ip not in multicast_addresses:
            multicast_addresses.add(multicast_ip)
            print(f"Multicast traffic detected on: {multicast_ip}")
            threading.Thread(target=listen_udp_multicast, args=(multicast_ip, port, listen_ip, forward_interface, src_mac, dst_mac, dst_port)).start()

def monitor_multicast_traffic(interface, port, listen_ip, forward_interface, src_mac, dst_mac, dst_port):
    print(f"Starting multicast traffic monitoring on interface: {interface}")
    sniff(iface=interface, prn=packet_callback, filter="ip multicast", store=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor multicast traffic on a network interface and forward it to another physical interface')
    parser.add_argument('-i', '--interface', dest='interface', type=str, required=True, help='Network interface to monitor')
    parser.add_argument('-p', '--port', dest='port', type=int, required=True, help='Port to listen on')
    parser.add_argument('-l', '--listen', dest='listen_ip', type=str, default='0.0.0.0', help='Local IP address to listen on')
    parser.add_argument('-fi', '--forward_interface', dest='forward_interface', type=str, required=True, help='Network interface to forward traffic to')
    parser.add_argument('--src_mac', dest='src_mac', type=str, required=True, help='Source MAC address for forwarded packets')
    parser.add_argument('--dst_mac', dest='dst_mac', type=str, required=True, help='Destination MAC address for forwarded packets')
    parser.add_argument('--dst_port', dest='dst_port', type=int, required=True, help='Destination port for forwarded packets')

    args = parser.parse_args()
    interface = args.interface
    port = args.port
    listen_ip = args.listen_ip
    forward_interface = args.forward_interface
    src_mac = args.src_mac
    dst_mac = args.dst_mac
    dst_port = args.dst_port

    monitor_multicast_traffic(interface, port, listen_ip, forward_interface, src_mac, dst_mac, dst_port)
