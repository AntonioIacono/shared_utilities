import socket
import struct
import time
import argparse
import threading

def createMessage(ipAddress,port,timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset,lifeenabled, checkenabled, life):
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
        print(array)
        value10 = struct.pack('B'* len(array), *array)
            
        value11 = struct.pack('>I',headerFcs)
        mettiInsieme = struct.pack('HH', protocolVersion, msgType)
        while len(dataset) % 8 != 0:
            dataset += '0'
        value12 = struct.pack('B', life)
        value13 = struct.pack('B', check)

        # Convert binary string to bytes
        value14 = bytes(int(dataset[i:i+8], 2) for i in range(0, len(dataset), 8))
        value15 = value12 + value13 + value14
        value7 = struct.pack('>I',len(value15))

        payload = value1+mettiInsieme+value4+value5+value6+value7+value8+value9+value10+value11+value15
        send_udp_packet(ipAddress, port, payload, time)
        time.sleep(timeValue/1004)


def send_udp_packet(ip_address, port, payload, time_value):

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Invio del pacchetto UDP
        udp_socket.sendto(payload, (ip_address, port))
        print(f"Pacchetto inviato a {ip_address}:{port}")
    except Exception as e:
        print(f"Errore durante l'invio del pacchetto: {e}")
    finally:
        # Chiusura del socket
        udp_socket.close()

def start_thread(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life):
    thread = threading.Thread(target=createMessage, args=(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life))
    thread.start()
    
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

    args = parser.parse_args()


    #createMessage(args.ipAddress, args.port, args.timeValue, args.sequenceCounter,
                  #args.protocolVersion, args.msgType, args.comId, args.etbTopoCnt, 
                  #args.opTrnTopoCnt, args.datasetLength, args.reserved01, args.replyComId, 
                  #args.replyIpAddress, args.headerFcs, args.dataset, args.lifeenabled, args.checkenabled, args.life)

    ip_multicast = "172.16.1.140"
    comid = 4003
    dataset_life = 200
    port = 17224
    dataset = "00000000000000000000000000000001111111111111111111111111101111111110101010110101101010101011111"
    
    """
    start_thread(ipAddress, port, timeValue, sequenceCounter, protocolVersion, msgType, 
                 comId, etbTopoCnt, opTrnTopoCnt, datasetLength, reserved01, replyComId, 
                 replyIpAddress, headerFcs, dataset, lifeenabled, checkenabled, life)
    """
    ##ComID 1301
    start_thread(239.13.1.1, port, dataset_life, 4035626, 1, 29264,               
                 1301, 0, 0, 4, 0, 1301,                                   
                 ip_multicast, 3572351821, dataset, True, True, 0)         
    ##ComID 1302
    #start_thread(???, port, dataset_life, 4035626, 1, 29264,               
    #             1302, 0, 0, 4, 0, 1302,                                   
    #             ip_multicast, 3572351821, dataset, True, True, 0)          
    ##ComID 1303
    #start_thread(???, port, dataset_life, 4035626, 1, 29264,               
    #             1303, 0, 0, 4, 0, 1303,                                   
    #             ip_multicast, 3572351821, dataset, True, True, 0)          
    
    ##NO Thread
    #createMessage(ip_multicast,port,dataset_life,4035626,1,29264,
    #              comid, 0,0,4,0,comid,
    #              ip_multicast, 3572351821,"00000000000000000000000000000001111111111111111111111111101111111110101010110101101010101011111",life_enabled,check,0)