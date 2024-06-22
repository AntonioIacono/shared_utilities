import socket
import struct
import time
import argparse
import threading
import random
import netifaces
import zlib

import random


def calculate_crc(data):
    """Calculate CRC32 using the zlib library."""
    return zlib.crc32(data) & 0xFFFFFFFF


def createMessage(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip, fuzzing_enabled, fuzz_fields):
    while True:
        sequenceCounter = sequenceCounter + 1
        life = life + 1 if lifeenabled else 1
        if life == 256:
            life = 0

        check = 1 if checkenabled else 0
        
        # Fuzzing fields
        if fuzzing_enabled:
            if 'sequenceCounter' in fuzz_fields:
                sequenceCounter = random.randint(0, 2**32 - 1)
            if 'protocolVersion' in fuzz_fields:
                protocolVersion = random.randint(0, 2**16 - 1)
            if 'msgType' in fuzz_fields:
                msgType = random.randint(0, 2**16 - 1)
            if 'comId' in fuzz_fields:
                comId = random.randint(0, 2**32 - 1)
            if 'etbTopoCnt' in fuzz_fields:
                etbTopoCnt = random.randint(0, 2**32 - 1)
            if 'opTrnTopoCnt' in fuzz_fields:
                opTrnTopoCnt = random.randint(0, 2**32 - 1)
            if 'reserved01' in fuzz_fields:
                reserved01 = random.randint(0, 2**32 - 1)
            if 'replyComId' in fuzz_fields:
                replyComId = random.randint(0, 2**32 - 1)
            if 'replyIpAddress' in fuzz_fields:
                replyIpAddress = '.'.join(str(random.randint(0, 255)) for _ in range(4))
            if 'dataset' in fuzz_fields:
                dataset = create_dataset(datasetLength - 2)
            if 'life' in fuzz_fields:
                life = random.randint(0, 255)
        
        value1 = struct.pack('>I', sequenceCounter)
        value4 = struct.pack('>I', comId)
        value5 = struct.pack('>I', etbTopoCnt)
        value6 = struct.pack('>I', opTrnTopoCnt)
        value8 = struct.pack('>I', reserved01)
        value9 = struct.pack('>I', replyComId)
        ipSplit = replyIpAddress.split('.')
        array = [int(value) for value in ipSplit]
        value10 = struct.pack('B' * len(array), *array)
        
        mettiInsieme = struct.pack('>HH', protocolVersion, msgType)
        while len(dataset) % 8 != 0:
            dataset += '0'
        value12 = struct.pack('B', life)
        value13 = struct.pack('B', check)
        value14 = bytes(int(dataset[i:i+8], 2) for i in range(0, len(dataset), 8))
        value15 = value12 + value13 + value14
        value7 = struct.pack('>I', len(value15))
        
        header_without_crc = value1 + struct.pack('<H', protocolVersion) + struct.pack('>H', msgType) + value4 + value5 + value6 + value7 + value8 + value9 + value10
        headerFcs = calculate_crc(header_without_crc)
        value11 = struct.pack('<I', headerFcs)
        
        payload = header_without_crc + value11 + value15
        send_udp_packet(ipAddress, port, payload, source_ip)
        time.sleep(timeValue / 1000)


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


def start_thread(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip):
    thread = threading.Thread(target=createMessage, args=(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip))
    thread.start()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send UDP packets with the specified parameters.')
    parser.add_argument('--fuzzing', action='store_true', help='Enable fuzzing')
    parser.add_argument('--fuzzfields', type=str, nargs='+', help='Fields to fuzz')
    # Other arguments...

    args = parser.parse_args()
    
    ip_multicast = "239.110.1.1"
    port = 17224
    dataset_life = 200
    sequenceCounter = 100
    protocolVersion = 1
    msgType = 20580
    comId = 1301
    etbTopoCnt = 0
    opTrnTopoCnt = 0
    datasetLength = random.randint(0, 2**32 - 1)
    reserved01 = 4
    replyComId = 0
    replyIpAddress = "0.0.0.0"
    headerFcs = 3572351821
    dataset = create_dataset(datasetLength - 2) # 2 bytes is for the header
    lifeenabled = True
    checkenabled = True
    life = 0
    fuzzing_enabled = True
    fuzz_fields = args.fuzzfields if args.fuzzfields else []

    interfaccia = "ens3"
    source_ip = wait_for_interface_ip(interfaccia, timeout=60, check_interval=1)
    
    start_thread(ip_multicast, port, dataset_life, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life, source_ip, fuzzing_enabled, fuzz_fields)
