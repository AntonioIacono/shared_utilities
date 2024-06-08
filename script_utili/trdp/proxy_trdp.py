import socket
import struct
import argparse
import threading
from scapy.all import sniff, sendp, Ether, IP, UDP

# Set di indirizzi multicast rilevati
detected_multicast_addresses = set()

def forward_packet(data, forward_interface, src_ip, dst_ip, dst_port):
    # Costruisce il pacchetto Ethernet
    ether = Ether()
    
    # Costruisce il pacchetto IP
    ip = IP(src=src_ip, dst=dst_ip)
    
    # Costruisce il pacchetto UDP
    udp = UDP(dport=dst_port, sport=dst_port)
    
    # Invia il pacchetto
    packet = ether / ip / udp / data
    sendp(packet, iface=forward_interface, verbose=0)

def listen_udp_multicast(multicast_ip, port, listen_ip, forward_interface, source_ip_forward):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind((listen_ip, port))

    # Unisce al gruppo multicast
    mreq = struct.pack('4s4s', socket.inet_aton(multicast_ip), socket.inet_aton(listen_ip))
    udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Ascolto su {multicast_ip}:{port} tramite {listen_ip}")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        print(f"Pacchetto ricevuto da {addr} su {multicast_ip}")

        # Inoltra direttamente il pacchetto
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
            print(f"Nuovo indirizzo multicast rilevato: {multicast_ip}")

def detect_multicast_addresses(interface, detection_time):
    print(f"Avvio del rilevamento degli indirizzi multicast sull'interfaccia: {interface} per {detection_time} secondi")
    
    # Monitora nuovi indirizzi multicast
    sniff(iface=interface, prn=packet_callback, filter="ip multicast", store=0, timeout=detection_time)

    print("Rilevamento completato. Indirizzi multicast rilevati:")
    for multicast_ip in detected_multicast_addresses:
        print(multicast_ip)

def start_listening_threads(port, listen_ip, forward_interface, source_ip_forward):
    for multicast_ip in detected_multicast_addresses:
        start_listening_thread(multicast_ip, port, listen_ip, forward_interface, source_ip_forward)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitora il traffico multicast su un\'interfaccia di rete e lo inoltra a un\'altra interfaccia fisica')
    parser.add_argument('-i', '--interface', dest='interface', type=str, default='ens3', help='Interfaccia di rete da monitorare')
    parser.add_argument('-p', '--port', dest='port', type=int, default=17224, help='Porta su cui ascoltare')
    parser.add_argument('-l', '--listen', dest='listen_ip', type=str, default='0.0.0.0', help='Indirizzo IP locale su cui ascoltare')
    parser.add_argument('-fi', '--forward_interface', dest='forward_interface', type=str, default='ens5', help='Interfaccia di rete su cui inoltrare il traffico')
    parser.add_argument('-fs', '--source_ip_forward', dest='source_ip_forward', type=str, default='172.23.0.13', help='Indirizzo IP da cui inoltrare il traffico')
    parser.add_argument('-t', '--detection_time', dest='detection_time', type=int, default=30, help='Tempo di rilevamento degli indirizzi multicast in secondi')

    args = parser.parse_args()
    interface = args.interface
    port = args.port
    listen_ip = args.listen_ip
    forward_interface = args.forward_interface
    source_ip_forward = args.source_ip_forward
    detection_time = args.detection_time

    # Fase di rilevamento degli indirizzi multicast
    detect_multicast_addresses(interface, detection_time)

    # Avvio dei thread di ascolto per gli indirizzi rilevati
    start_listening_threads(port, listen_ip, forward_interface, source_ip_forward)
