import socket
import struct
import time
import argparse
import threading
import random
import netifaces
import zlib


def calculate_crc(data):
    """Calculate CRC32 using the zlib library."""
    return zlib.crc32(data) & 0xFFFFFFFF


def createMessage(ipAddress,port,timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset,lifeenabled, checkenabled, life, source_ip):
    while True:
        sequenceCounter = sequenceCounter + 1
        life = life + 1 if lifeenabled else 1
        if life == 256:
            life = 0

        check = 1 if checkenabled else 0
        value1 = struct.pack('>I',sequenceCounter)

        value4 = struct.pack('>I',comId)
        value5 = struct.pack('>I',etbTopoCnt)
        value6 = struct.pack('>I',opTrnTopoCnt)
    
        value8 = struct.pack('>I',reserved01)
        value9 = struct.pack('>I',replyComId)
        ipSplit = replyIpAddress.split('.')
        i = 0
        array = []
        for value in ipSplit:
            array.append(int(value))
        values_to_pack = [valore for valore in array]
        #print(array)
        value10 = struct.pack('B'* len(array), *array)
            
        
        mettiInsieme = struct.pack('>HH', protocolVersion, msgType)
        while len(dataset) % 8 != 0:
            dataset += '0'
        value12 = struct.pack('B', life)
        value13 = struct.pack('B', check)

        # Convert binary string to bytes
        value14 = bytes(int(dataset[i:i+8], 2) for i in range(0, len(dataset), 8))
        value15 = value12 + value13 + value14
        value7 = struct.pack('>I',len(value15))

        # Construct the header without the CRC
        header_without_crc = value1 + struct.pack('<H', protocolVersion) + struct.pack('>H', msgType) + value4 + value5 + value6 + value7 + value8 + value9 + value10
        # Calculate the CRC over the header
        #headerFcs = fcs32(header_without_crc, 32, headerFcs)
        headerFcs = calculate_crc(header_without_crc)
        value11 = struct.pack('<I', headerFcs)

        # Complete header with CRC and payload
        payload = header_without_crc + value11 + value15
        send_udp_packet(ipAddress, port, payload, source_ip)
        time.sleep(timeValue/1000)

def send_udp_packet(ip_address, port, payload, source_ip):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((source_ip, 0))
    # Set the TTL (Time-To-Live)
    ttl = struct.pack('B', 64)  # unsigned char as 1-byte object
    udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    try:
        # Invio del pacchetto UDP
        udp_socket.sendto(payload, (ip_address, port))
        print(f"Packet sent to {ip_address}:{port}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Chiusura del socket
        udp_socket.close()

def start_thread(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip):
    thread = threading.Thread(target=createMessage, args=(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip))
    thread.start()

def create_dataset(dataset_length):
    num_bits = dataset_length * 8
    dataset = ''.join(random.choice('01') for _ in range(num_bits))
    return dataset

def check_interface_ip(interface):
    try:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            ip_info = addresses[netifaces.AF_INET][0]
            ip_address = ip_info.get('addr', None)
            if ip_address:
                return ip_address
        return None
    except ValueError:
        return None

def wait_for_interface_ip(interface, timeout=60, check_interval=1):
    start_time = time.time()
    while True:
        ip_address = check_interface_ip(interface)
        if ip_address:
            return ip_address
        if time.time() - start_time > timeout:
            return None
        time.sleep(check_interval)


if __name__ == '__main__':

    # Setup the command line arguments.
    parser = argparse.ArgumentParser(description='Send UDP packets with the specified parameters.')
    parser.add_argument('-i', '--ip', dest='ipAddress', type=str, required=False, help='IP Multicast Address')
    parser.add_argument('-p', '--port', dest='port', type=int, required=False, help='Port UDP')
    parser.add_argument('-t', '--time', dest='timeValue', type=int, required=False, help='Time value between packets')
    parser.add_argument('-s', '--sequence', dest='sequenceCounter', type=int, default=0, required=False, help='Initial sequence counter value')
    parser.add_argument('--protocol', dest='protocolVersion', type=int, required=False, help='Protocol version')
    parser.add_argument('--msgtype', dest='msgType', type=int, required=False, help='Message type')
    parser.add_argument('--comid', dest='comId', type=int, required=False, help='Comunication ID')
    parser.add_argument('--etb', dest='etbTopoCnt', type=int, default=0, required=False, help='ETB Topo Counter')
    parser.add_argument('--optrn', dest='opTrnTopoCnt', type=int, default=0, required=False, help='Op Trn Topo Counter')
    parser.add_argument('--length', dest='datasetLength', type=int, required=False, help='Dataset length')
    parser.add_argument('--reserved', dest='reserved01', type=int, default=0, required=False, help='Reserved')
    parser.add_argument('--replyid', dest='replyComId', type=int, required=False, help='Comunication ID reply')
    parser.add_argument('--replyip', dest='replyIpAddress', type=str, required=False, help='IP address reply')
    parser.add_argument('--fcs', dest='headerFcs', type=int, required=False, help='Header FCS')
    parser.add_argument('--dataset', dest='dataset', type=str, required=False, help='Binary dataset format')
    parser.add_argument('--lifeenabled', action='store_true', required=False, help='Enable life field increment')
    parser.add_argument('--checkenabled', action='store_true', required=False, help='Enable check field')
    parser.add_argument('--life', dest='life', type=int, default=0, required=False, help='Initial value of field life')
    parser.add_argument('--interface', dest='interface', type=str, default=0, required=False, help='Network interface')
    args = parser.parse_args()




    
"""
start_thread(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, 
                comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
                replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life)
"""


#msgType=29264 -> ENA request
#msgType=28752 -> ENA replay


#Wait for interfaces set up
interfaccia_mdcu_A = "ens3" #172.16.2.41
source_ip_mdcu_A = wait_for_interface_ip(interfaccia_mdcu_A, timeout=60, check_interval=1)

interfaccia_mdcu_B = "ens4" #172.16.2.41
source_ip_mdcu_B = wait_for_interface_ip(interfaccia_mdcu_B, timeout=60, check_interval=1)

interfaccia_ena_A = "ens5" #172.16.1.145
source_ip_ena_A = wait_for_interface_ip(interfaccia_ena_A, timeout=60, check_interval=1)

interfaccia_ena_B = "ens6" #172.16.2.145
source_ip_ena_B = wait_for_interface_ip(interfaccia_ena_B, timeout=60, check_interval=1)

## Parameters dataset with ComID 40003
ip_multicast = "239.13.1.1"
port = 17224
dataset_life = 200
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20580
comId = 40003
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 48
reserved01 = 4
replyComId = 0
replyIpAddress = "0.0.0.0"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip_mdcu_A)

## Parameters dataset with ComID 20008
ip_multicast = "239.13.1.1"
port = 17224
dataset_life = 50
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20580
comId = 20008
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 24 #to be defined
reserved01 = 4
replyComId = 0
replyIpAddress = "0.0.0.0"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

#start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
#            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
#            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip)


## Parameters dataset with ComID 13010
ip_multicast = "239.21.1.12"
port = 17224
dataset_life = 200
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20594
comId = 13010
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 12
reserved01 = 4
replyComId = 1301
replyIpAddress = "239.110.1.1"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip_ena_A)

## Parameters dataset with ComID 13030
ip_multicast = "239.21.1.12"
port = 17224
dataset_life = 10000
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20594
comId = 13030
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 12
reserved01 = 4
replyComId = 1303
replyIpAddress = "239.110.1.1"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip_ena_A)

#Unauthorized dataset
## Parameters dataset with ComID 40003
ip_multicast = "239.13.1.1"
port = 17224
dataset_life = 1000
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20580
comId = 40003
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 450 
reserved01 = 4
replyComId = 0
replyIpAddress = "0.0.0.0"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip_mdcu_A)

#Unauthorized dataset
## Parameters dataset with ComID 40009
ip_multicast = "239.13.1.1"
port = 17224
dataset_life = 1000
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20580
comId = 40009
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 450 
reserved01 = 4
replyComId = 0
replyIpAddress = "0.0.0.0"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip_ena_A)



##########
# VLAN B #
##########


## Parameters dataset with ComID 40003
ip_multicast = "239.13.2.1"
port = 17224
dataset_life = 200
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20580
comId = 40003
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 48
reserved01 = 4
replyComId = 0
replyIpAddress = "0.0.0.0"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip_mdcu_B)




## Parameters dataset with ComID 13010
ip_multicast = "239.21.2.12"
port = 17224
dataset_life = 200
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20594
comId = 13010
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 12
reserved01 = 4
replyComId = 1301
replyIpAddress = "239.110.1.1"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip_ena_B)

## Parameters dataset with ComID 13030
ip_multicast = "239.21.2.12"
port = 17224
dataset_life = 10000
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20594
comId = 40003
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 12
reserved01 = 4
replyComId = 1303
replyIpAddress = "239.110.1.1"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip_ena_B)

#Unauthorized dataset
## Parameters dataset with ComID 40003
ip_multicast = "239.13.2.1"
port = 17224
dataset_life = 1000
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20580
comId = 40003
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 450 
reserved01 = 4
replyComId = 0
replyIpAddress = "0.0.0.0"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip_mdcu_B)

#Unauthorized dataset
## Parameters dataset with ComID 40009
ip_multicast = "239.13.2.1"
port = 17224
dataset_life = 1000
sequenceCounter = 4035626
protocolVersion = 1
msgType = 20580
comId = 40009
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 450 
reserved01 = 4
replyComId = 0
replyIpAddress = "0.0.0.0"
headerFcs = 3572351821
dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
lifeenabled = True
checkenabled = True
life = 0

start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, 
            comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip_ena_B)
