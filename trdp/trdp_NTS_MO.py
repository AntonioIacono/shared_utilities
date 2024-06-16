import socket
import struct
import time
import argparse
import threading
import random
import netifaces

fcstab = [
0x00000000, 0x77073096, 0xee0e612c, 0x990951ba,
0x076dc419, 0x706af48f, 0xe963a535, 0x9e6495a3,
0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988,
0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91,
0x1db71064, 0x6ab020f2, 0xf3b97148, 0x84be41de,
0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec,
0x14015c4f, 0x63066cd9, 0xfa0f3d63, 0x8d080df5,
0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172,
0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b,
0x35b5a8fa, 0x42b2986c, 0xdbbbc9d6, 0xacbcf940,
0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116,
0x21b4f4b5, 0x56b3c423, 0xcfba9599, 0xb8bda50f,
0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924,
0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d,
0x76dc4190, 0x01db7106, 0x98d220bc, 0xefd5102a,
0x71b18589, 0x06b6b51f, 0x9fbfe4a5, 0xe8b8d433,
0x7807c9a2, 0x0f00f934, 0x9609a88e, 0xe10e9818,
0x7f6a0dbb, 0x086d3d2d, 0x91646c97, 0xe6635c01,
0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e,
0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457,
0x65b0d9c6, 0x12b7e950, 0x8bbeb8ea, 0xfcb9887c,
0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65,
0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2,
0x4adfa541, 0x3dd895d7, 0xa4d1c46d, 0xd3d6f4fb,
0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0,
0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9,
0x5005713c, 0x270241aa, 0xbe0b1010, 0xc90c2086,
0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f,
0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4,
0x59b33d17, 0x2eb40d81, 0xb7bd5c3b, 0xc0ba6cad,
0xedb88320, 0x9abfb3b6, 0x03b6e20c, 0x74b1d29a,
0xead54739, 0x9dd277af, 0x04db2615, 0x73dc1683,
0xe3630b12, 0x94643b84, 0x0d6d6a3e, 0x7a6a5aa8,
0xe40ecf0b, 0x9309ff9d, 0x0a00ae27, 0x7d079eb1,
0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe,
0xf762575d, 0x806567cb, 0x196c3671, 0x6e6b06e7,
0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc,
0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5,
0xd6d6a3e8, 0xa1d1937e, 0x38d8c2c4, 0x4fdff252,
0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b,
0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60,
0xdf60efc3, 0xa867df55, 0x316e8eef, 0x4669be79,
0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236,
0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f,
0xc5ba3bbe, 0xb2bd0b28, 0x2bb45a92, 0x5cb36a04,
0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d,
0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x026d930a,
0x9c0906a9, 0xeb0e363f, 0x72076785, 0x05005713,
0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0x0cb61b38,
0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0x0bdbdf21,
0x86d3d2d4, 0xf1d4e242, 0x68ddb3f8, 0x1fda836e,
0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777,
0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c,
0x8f659eff, 0xf862ae69, 0x616bffd3, 0x166ccf45,
0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2,
0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db,
0xaed16a4a, 0xd9d65adc, 0x40df0b66, 0x37d83bf0,
0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9,
0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6,
0xbad03605, 0xcdd70693, 0x54de5729, 0x23d967bf,
0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94,
0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d
]

def fcs32(buf, len, fcs):
    for i in range(len):
        fcs = (fcs >> 8) ^ fcstab[(fcs ^ buf[i]) & 0xff]
    return fcs



def createMessage(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip):
    while True:
        sequenceCounter += 1
        life = (life + 1) if lifeenabled else 1
        if life == 256:
            life = 0

        check = 1 if checkenabled else 0

        # Pack fields
        value1 = struct.pack('>I', sequenceCounter)
        value4 = struct.pack('>I', comId)
        value5 = struct.pack('>I', etbTopoCnt)
        value6 = struct.pack('>I', opTrnTopoCnt)
        value8 = struct.pack('>I', reserved01)
        value9 = struct.pack('>I', replyComId)
        
        # Pack IP address
        ipSplit = list(map(int, replyIpAddress.split('.')))
        value10 = struct.pack('BBBB', *ipSplit)

        value12 = struct.pack('B', life)
        value13 = struct.pack('B', check)

        # Ensure dataset is a multiple of 8 bits
        while len(dataset) % 8 != 0:
            dataset += '0'
        
        # Convert binary string to bytes
        value14 = bytes(int(dataset[i:i+8], 2) for i in range(0, len(dataset), 8))
        value15 = value12 + value13 + value14

        # Calculate dataset length and pack it
        datasetLength = len(value15)
        value7 = struct.pack('>I', datasetLength)

        # Construct the header without the CRC
        header_without_crc = value1 + struct.pack('HH', protocolVersion, msgType) + value4 + value5 + value6 + value7 + value8 + value9 + value10
        print(len(header_without_crc))
        # Calculate the CRC over the header
        #headerFcs = fcs32(header_without_crc, 32, headerFcs)
        value11 = struct.pack('>I', headerFcs)

        # Complete header with CRC and payload
        payload = header_without_crc + value11 + value15

        # Send the packet
        send_udp_packet(ipAddress, port, payload, source_ip)

        # Sleep for the specified time interval
        time.sleep(timeValue / 1000.0)


def send_udp_packet(ip_address, port, payload, source_ip):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((source_ip, 0))
    try:
        # Invio del pacchetto UDP
        udp_socket.sendto(payload, (ip_address, port))
        #print(f"Packet sent to {ip_address}:{port}")
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


    #Wait for interfaces set up
    # Esempio di utilizzo
interfaccia = "ens3"
source_ip = wait_for_interface_ip(interfaccia, timeout=60, check_interval=1)
    
"""
start_thread(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, 
                comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
                replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life)
"""


#msgType=29264 -> ENA request
#msgType=28752 -> ENA replay


## Parameters dataset with ComID 1301
ip_multicast = "239.110.1.1"
port = 17224
dataset_life = 200
sequenceCounter = 4035626
protocolVersion = 1
msgType = 28752
comId = 1301
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 500
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
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip)

## Parameters dataset with ComID 1303
ip_multicast = "239.110.1.1"
port = 17224
dataset_life = 10000
sequenceCounter = 4035626
protocolVersion = 1
msgType = 28752
comId = 1303
etbTopoCnt = 0
opTrnTopoCnt = 0
datasetLength = 350 
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
            replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip)


