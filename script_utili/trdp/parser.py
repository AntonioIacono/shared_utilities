import socket
import struct
import argparse

def parse_trdp_packet(data):
    # Estrarre i campi dai pacchetti TRDP
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

def listen_udp(ip, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((ip, port))

    print(f"Listening on {ip}:{port}")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        print(f"Received packet from {addr}")

        parsed_packet = parse_trdp_packet(data)
        for key, value in parsed_packet.items():
            print(f"{key}: {value}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TRDP UDP Listener')
    parser.add_argument('-i', '--ip', dest='ip', type=str, required=True, help='IP address to listen on')
    parser.add_argument('-p', '--port', dest='port', type=int, required=True, help='Port to listen on')

    args = parser.parse_args()
    listen_udp(args.ip, args.port)
