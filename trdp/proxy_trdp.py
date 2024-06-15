import argparse
import threading
import struct
import netifaces
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
   
    # Calculate the size of the TRDP packet
    trdp_packet_size = len(data)

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
        'dataset': dataset,
        'packetSize' : trdp_packet_size
    }

def forward_packet(packet, forward_interface, new_dest_ip):
    packet[IP].src = source_ip
    packet[IP].dst = new_dest_ip
    sendp(packet, iface=forward_interface, verbose=0)

def packet_worker(q, forward_interface1, forward_interface2 = None):
    while True:
        packet = q.get()
        new_ip_to_MN = "239.100.1.1"
        new_ip_to_ON_A = "239.24.1.1"
        new_ip_to_ON_B = "239.24.2.1"
        # Here there is a list of ACL based first on IP and then on TRDP parameters
        if IP in packet and Raw in packet:
        #################################
        # ACL from VLAN_A to Multimedia #
        #################################
            if packet[IP].dst == "239.13.1.1":
                data = bytes(packet[Raw])
                parsed_packet = parse_trdp_packet(data)
                #dataset comID 40003
                if parsed_packet['comId'] == 40003 and parsed_packet['packetSize'] == 48 and parsed_packet:
                    forward_packet(packet, forward_interface1, new_ip_to_MN)

            if packet[IP].dst == "239.21.1.12":
                data = bytes(packet[Raw])
                parsed_packet = parse_trdp_packet(data)
                #dataset comID 13010
                if parsed_packet['comId'] == 13010 and parsed_packet['packetSize'] == 12 and parsed_packet:
                    forward_packet(packet, forward_interface1, new_ip_to_MN)   

                #dataset comID 13030
                if parsed_packet['comId'] == 13030 and parsed_packet['packetSize'] == 12 and parsed_packet:
                    forward_packet(packet, forward_interface1, new_ip_to_MN) 
        
        #################################
        # ACL from VLAN_B to Multimedia #
        #################################
            if packet[IP].dst == "239.13.2.1":
                data = bytes(packet[Raw])
                parsed_packet = parse_trdp_packet(data)
                #dataset comID 40003
                if parsed_packet['comId'] == 40003 and parsed_packet['packetSize'] == 48 and parsed_packet:
                    forward_packet(packet, forward_interface1, new_ip_to_MN)

            if packet[IP].dst == "239.21.2.12":
                data = bytes(packet[Raw])
                parsed_packet = parse_trdp_packet(data)
                #dataset comID 13010
                if parsed_packet['comId'] == 13010 and parsed_packet['packetSize'] == 12 and parsed_packet:
                    forward_packet(packet, forward_interface1, new_ip_to_MN)   

                #dataset comID 13030
                if parsed_packet['comId'] == 13030 and parsed_packet['packetSize'] == 12 and parsed_packet:
                    forward_packet(packet, forward_interface1, new_ip_to_MN)

        #############################################
        # ACL from  Multimedia to VLAN_A and VLAN_B #
        #############################################
            if packet[IP].dst == '239.110.1.1':
                data = bytes(packet[Raw])
                parsed_packet = parse_trdp_packet(data)
                print(parsed_packet['comId'])
                print(parsed_packet['packetSize'])
                #dataset comID 1301
                if parsed_packet['comId'] == 1301 and parsed_packet['packetSize'] == 500 and parsed_packet:
                    print ("pacchetto")
                    forward_packet(packet, forward_interface1, new_ip_to_ON_A)
                    forward_packet(packet, forward_interface2, new_ip_to_ON_B)   

                #dataset comID 1303
                if parsed_packet['comId'] == 1303 and parsed_packet['packetSize'] == 350 and parsed_packet:
                    print ("pacchetto")
                    forward_packet(packet, forward_interface1, new_ip_to_ON_A)
                    forward_packet(packet, forward_interface2, new_ip_to_ON_B)         
        q.task_done()

def monitor_and_forward(interface, forward_interface1, forward_interface2 = None):
    print(f"Monitoring and forwarding multicast UDP traffic from {interface} to {forward_interface1} {forward_interface2}")
    
    # Aumentiamo la dimensione della coda
    packet_queue = Queue(maxsize=100000)  # Possiamo regolare la dimensione della coda a seconda delle esigenze

    # Avvio i thread lavoratori
    for _ in range(200):  # Possiamo regolare il numero di thread a seconda delle esigenze
        t = threading.Thread(target=packet_worker, args=(packet_queue, forward_interface1,forward_interface2), daemon=True)
        t.start()

    # Callback per sniffing e invio dei pacchetti alla coda
    sniff(iface=interface, prn=lambda x: packet_queue.put(x), filter="udp and multicast", store=0)


def get_interface_ip(interface):
    """Ottieni l'indirizzo IP dell'interfaccia specificata."""
    addresses = netifaces.ifaddresses(interface)
    return addresses[netifaces.AF_INET][0]['addr']


def start_monitoring(interface1, interface2, interface3):
    threads = []
    
    # Start the first monitor_and_forward call
    t1 = threading.Thread(target=monitor_and_forward, args=(interface1, interface3))
    threads.append(t1)
    
    # Start the second monitor_and_forward call
    t2 = threading.Thread(target=monitor_and_forward, args=(interface2, interface3))
    threads.append(t2)
    
    # Start the third monitor_and_forward call
    t3 = threading.Thread(target=monitor_and_forward, args=(interface3, interface1, interface2))
    threads.append(t3)
    
    # Start all threads
    for t in threads:
        t.start()
    
    # Join all threads
    for t in threads:
        t.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple script to sniff and forward UDP multicast traffic from one interface to another')
    parser.add_argument('-a', '--interface_A', dest='interface_A', type=str, default='ens3', help='Source network interface to sniff multicast UDP traffic from')
    parser.add_argument('-b', '--interface_B', dest='interface_B', type=str, default='ens4', help='Source network interface to sniff multicast UDP traffic from')
    parser.add_argument('-m', '--interface_M', dest='interface_M', type=str, default='ens5', help='Source network interface to sniff multicast UDP traffic from')
    parser.add_argument('-fi', '--forward_interface', dest='forward_interface', type=str, default='ens5', help='Network interface to forward traffic to')
    parser.add_argument('-src', '--source_ip', dest='source_ip', type=str, default=get_interface_ip('ens5'), help='New source IP address for forwarded packets (optional)')
    
    args = parser.parse_args()
    interface1 = args.interface_A
    interface2 = args.interface_B
    interface3 = args.interface_M    
   
    source_ip = args.source_ip
    #monitor_and_forward(interface1, interface3)
    #monitor_and_forward(interface2, interface3)
    #monitor_and_forward(interface3, interface1, interface2)

    start_monitoring(interface1, interface2, interface3)