#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>

#define BUFFER_SIZE 1024

// Set of multicast addresses to filter
char *multicast_addresses[] = {"239.18.1.1", "239.18.1.10", "239.13.1.1", "239.13.1.10"};
int num_multicast_addresses = 4;
int detected_multicast_addresses[num_multicast_addresses];

void forward_packet(char *data, char *forward_interface, char *src_ip, char *dst_ip, int dst_port) {
    // Build the Ethernet packet
    // ...

    // Build the IP packet
    struct in_addr src_addr, dst_addr;
    inet_aton(src_ip, &src_addr);
    inet_aton(dst_ip, &dst_addr);
    struct iphdr *ip = malloc(sizeof(struct iphdr));
    ip->saddr = src_addr.s_addr;
    ip->daddr = dst_addr.s_addr;

    // Build the UDP packet
    struct udphdr *udp = malloc(sizeof(struct udphdr));
    udp->dest = htons(dst_port);
    udp->source = htons(dst_port);

    // Send the packet
    // ...
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
        forward_packet(buffer, forward_interface, source_ip_forward, multicast_ip, port);
    }

    close(udp_socket);
    return NULL;
}

void *start_listening_thread(void *arg) {
    char *multicast_ip = (char *)arg;
    pthread_t thread;
    if (pthread_create(&thread, NULL, listen_udp_multicast, multicast_ip) != 0) {
        perror("pthread_create");
        return NULL;
    }
    return (void *)thread;
}

void packet_callback(char *packet, int len) {
    struct iphdr *ip = (struct iphdr *)packet;
    if (ip->version == 4 && ip->daddr >> 24 == 0xef) {
        char *multicast_ip = inet_ntoa(*(struct in_addr *)&ip->daddr);
        int i;
        for (i = 0; i < num_multicast_addresses; i++) {
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
    int i;
    for (i = 0; i < num_multicast_addresses; i++) {
        start_listening_thread(multicast_addresses[i]);
    }

    // Monitor for new multicast addresses
    // ...
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

