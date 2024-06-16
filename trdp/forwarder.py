import scapy.all as scapy
from scapy.layers.l2 import Ether
import argparse

def forward_packet(packet, output_interface):
    try:
        scapy.sendp(packet, iface=output_interface, verbose=False)
        print(f"Packet forwarded to {output_interface}")
    except Exception as e:
        print(f"Error forwarding packet: {e}")

def packet_callback(packet, output_interface):
    forward_packet(packet, output_interface)

def main(input_interface, output_interface):
    print(f"Listening on {input_interface} and forwarding to {output_interface}")
    scapy.sniff(iface=input_interface, prn=lambda packet: packet_callback(packet, output_interface))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Packet forwarder script")
    parser.add_argument("input_interface", help="Input network interface to listen on")
    parser.add_argument("output_interface", help="Output network interface to forward packets to")

    args = parser.parse_args()

    main(args.input_interface, args.output_interface)
