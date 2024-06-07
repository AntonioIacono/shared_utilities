#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <netinet/ip.h>
#include <netinet/udp.h>
#include <ifaddrs.h>
#include <linux/if_packet.h>
#include <net/ethernet.h>
#include <net/if.h>
#include <sys/ioctl.h>

#define BUFFER_SIZE 1024

// Set of multicast addresses to filter
char *multicast_addresses[] = {"239.18.1.1", "239.18.1.10", "239.13.1.1", "239.13.1.10"};
int num_multicast_addresses = 4;
int detected_multicast_addresses[4] = {0};  // Array to track detected addresses

#include <netinet/in.h>
#include <arpa/inet.h>

void forward_packet(char *data, int len, char *forward_interface, char *src_ip, char *dst_ip, int dst_port) {
    // Create a raw socket
    int sockfd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (sockfd < 0) {
        perror("socket");
        return;
    }

    struct ifreq if_idx;
    memset(&if_idx, 0, sizeof(struct ifreq));
    strncpy(if_idx.ifr_name, forward_interface, IFNAMSIZ - 1);
    if (ioctl(sockfd, SIOCGIFINDEX, &if_idx) < 0) {
        perror("SIOCGIFINDEX");
        close(sockfd);
        return;
    }

    struct sockaddr_ll sa;
    memset(&sa, 0, sizeof(struct sockaddr_ll));
    sa.sll_family = AF_PACKET;
    sa.sll_ifindex = if_idx.ifr_ifindex;
    sa.sll_protocol = htons(ETH_P_IP);

    // Set the source IP address in the IP header
    struct iphdr *ip_hdr = (struct iphdr *)(data + sizeof(struct ethhdr));
    ip_hdr->saddr = inet_addr(src_ip);

    // Send the packet
    if (sendto(sockfd, data, len, 0, (struct sockaddr*)&sa, sizeof(struct sockaddr_ll)) < 0) {
        perror("sendto");
    }

    close(sockfd);
}

void *listen_udp_multicast(void *arg) {
    char *multicast_ip = (char *)arg;
    int port = 17224;
    char *listen_ip = "0.0.0.0";
    char *forward_interface = "ens5";
    char *source_ip_forward = "172.23.0.13";

    int udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udp_socket < 0) {
        perror("socket");
        return NULL;
    }

    int reuse = 1;
    if (setsockopt(udp_socket, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
        perror("setsockopt");
        close(udp_socket);
        return NULL;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = inet_addr(listen_ip);
    addr.sin_port = htons(port);

    if (bind(udp_socket, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(udp_socket);
        return NULL;
    }

    struct ip_mreq mreq;
    inet_aton(multicast_ip, &mreq.imr_multiaddr);
    inet_aton(listen_ip, &mreq.imr_interface);
    if (setsockopt(udp_socket, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
        perror("setsockopt");
        close(udp_socket);
        return NULL;
    }

    printf("Listening on %s:%d via %s\n", multicast_ip, port, listen_ip);

    char buffer[BUFFER_SIZE];
    struct sockaddr_in client_addr;
    socklen_t client_addr_len = sizeof(client_addr);

    while (1) {
        int bytes_received = recvfrom(udp_socket, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&client_addr, &client_addr_len);
        if (bytes_received < 0) {
            perror("recvfrom");
            continue;
        }

        printf("Received packet from %s on %s\n", inet_ntoa(client_addr.sin_addr), multicast_ip);

        // Directly forward the packet
        forward_packet(buffer, bytes_received, forward_interface, source_ip_forward, multicast_ip, port);
    }

    close(udp_socket);
    return NULL;
}

void start_listening_thread(char *multicast_ip) {
    pthread_t thread;
    char *ip_copy = strdup(multicast_ip);  // Allocate memory for the IP address
    if (pthread_create(&thread, NULL, listen_udp_multicast, ip_copy) != 0) {
        perror("pthread_create");
        free(ip_copy);  // Free memory on error
    } else {
        pthread_detach(thread);  // Detach thread to handle it independently
    }
}

void packet_callback(char *packet, int len) {
    struct iphdr *ip = (struct iphdr *)packet;
    if (ip->version == 4 && (ntohl(ip->daddr) >> 24) == 0xef) {
        char multicast_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &ip->daddr, multicast_ip, INET_ADDRSTRLEN);
        for (int i = 0; i < num_multicast_addresses; i++) {
            if (strcmp(multicast_ip, multicast_addresses[i]) == 0) {
                if (detected_multicast_addresses[i] == 0) {
                    detected_multicast_addresses[i] = 1;
                    printf("New multicast address detected: %s\n", multicast_ip);
                    start_listening_thread(multicast_ip);
                }
                break;
            }
        }
    }
}

void monitor_multicast_traffic(char *interface, int port, char *listen_ip, char *forward_interface, char *source_ip_forward) {
    printf("Starting multicast traffic monitoring on interface: %s\n", interface);

    // Start threads for predefined multicast addresses
    for (int i = 0; i < num_multicast_addresses; i++) {
        start_listening_thread(multicast_addresses[i]);
    }

    // Monitor for new multicast addresses
    // This is a placeholder for actual packet capture implementation
    // For example, using pcap or similar library to capture packets and call packet_callback
    while (1) {
        // Simulate packet reception for demonstration purposes
        // In practice, replace with actual packet capture and handling
        char dummy_packet[BUFFER_SIZE];
        int dummy_len = BUFFER_SIZE;
        packet_callback(dummy_packet, dummy_len);
        sleep(1);  // Adjust as needed for actual implementation
    }
}

int main(int argc, char *argv[]) {
    char *interface = "ens3";
    int port = 17224;
    char *listen_ip = "0.0.0.0";
    char *forward_interface = "ens5";
    char *source_ip_forward = "172.23.0.13";

    monitor_multicast_traffic(interface, port, listen_ip, forward_interface, source_ip_forward);

    return 0;
}
