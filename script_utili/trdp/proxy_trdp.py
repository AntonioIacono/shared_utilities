import socket
import struct
import argparse
import threading
from scapy.all import sniff, sendp, Ether, IP, UDP

multicast_addresses = set()

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

def forward_packet(data, forward_interface, src_ip, dst_ip, dst_port):
    ether = Ether()
    ip = IP(src=src_ip, dst=dst_ip)
    udp = UDP(dport=dst_port, sport=dst_port)
    packet = ether / ip / udp / data
    sendp(packet, iface=forward_interface, verbose=0)

def listen_udp_multicast(multicast_ip, port, listen_ip, forward_interface, source_ip_forward):
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    raw_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    raw_socket.bind((listen_ip, port))

    mreq = struct.pack('4s4s', socket.inet_aton(multicast_ip), socket.inet_aton(listen_ip))
    raw_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Listening on {multicast_ip}:{port} via {listen_ip}")

    while True:
        data, addr = raw_socket.recvfrom(65535)
        print(f"Received packet from {addr} on {multicast_ip}")

        parsed_packet = parse_trdp_packet(data[28:])  # IP header is 20 bytes, UDP header is 8 bytes
        for key, value in parsed_packet.items():
            print(f"{key}: {value}")
        if parsed_packet['comId'] == 40003:
            forward_packet(data[28:], forward_interface, source_ip_forward, multicast_ip, port)

def packet_callback(packet):
    if IP in packet and (packet[IP].dst.startswith("239.")):
        multicast_ip = packet[IP].dst
        if multicast_ip not in multicast_addresses:
            multicast_addresses.add(multicast_ip)
            print(f"Multicast traffic detected on: {multicast_ip}")
            threading.Thread(target=listen_udp_multicast, args=(multicast_ip, port, listen_ip, forward_interface, source_ip_forward)).start()

def monitor_multicast_traffic(interface, port, listen_ip, forward_interface, source_ip_forward):
    print(f"Starting multicast traffic monitoring on interface: {interface}")
    sniff(iface=interface, prn=packet_callback, filter="ip multicast", store=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor multicast traffic on a network interface and forward it to another physical interface')
    parser.add_argument('-i', '--interface', dest='interface', type=str, default='ens3', help='Network interface to monitor')
    parser.add_argument('-p', '--port', dest='port', type=int, default='17224', help='Port to listen on')
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
