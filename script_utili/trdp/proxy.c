#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>

#define BUFFER_SIZE 1024

char *multicast_addresses[] = {"239.18.1.1", "239.18.1.10", "239.13.1.1", "239.13.1.10"};
int num_multicast_addresses = 4;
int detected_multicast_addresses[4] = {0};

void forward_packet(char *data, int len, char *forward_interface, char *src_ip, char *dst_ip, int dst_port) {
    // Estrarre l'indirizzo IP di destinazione dal pacchetto originale
    struct iphdr *ip_hdr = (struct iphdr *)(data + sizeof(struct ethhdr));
    char dst_ip_from_packet[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &(ip_hdr->daddr), dst_ip_from_packet, INET_ADDRSTRLEN);

    // Utilizzare l'indirizzo IP di destinazione estratto per impostare l'indirizzo di destinazione nel pacchetto inoltrato
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(dst_port);
    addr.sin_addr.s_addr = inet_addr(dst_ip_from_packet); // Usare l'indirizzo IP di destinazione estratto

    // Set the source IP address in the IP header
    struct sockaddr_in source_addr;
    memset(&source_addr, 0, sizeof(source_addr));
    source_addr.sin_family = AF_INET;
    source_addr.sin_addr.s_addr = inet_addr(src_ip);

    // Invia il pacchetto inoltrato
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return;
    }

    if (bind(sockfd, (struct sockaddr*)&source_addr, sizeof(source_addr)) < 0) {
        perror("bind");
        close(sockfd);
        return;
    }

    if (sendto(sockfd, data, len, 0, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("sendto");
    }

    close(sockfd);
}


void *listen_udp_multicast(void *arg) {
    char *multicast_ip = (char *)arg;
    int port = 17224;

    int udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (udp_socket < 0) {
        perror("socket");
        return NULL;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY; // Listen on any interface
    addr.sin_port = htons(port);

    if (bind(udp_socket, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(udp_socket);
        return NULL;
    }

    struct ip_mreq mreq;
    inet_aton(multicast_ip, &mreq.imr_multiaddr);
    mreq.imr_interface.s_addr = htonl(INADDR_ANY);
    if (setsockopt(udp_socket, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
        perror("setsockopt");
        close(udp_socket);
        return NULL;
    }

    printf("Listening on %s:%d\n", multicast_ip, port);

    char buffer[BUFFER_SIZE];
    struct sockaddr_in client_addr;
    socklen_t client_addr_len = sizeof(client_addr);

    while (1) {
        int bytes_received = recvfrom(udp_socket, buffer, BUFFER_SIZE, 0, (struct sockaddr *)&client_addr, &client_addr_len);
        if (bytes_received < 0) {
            perror("recvfrom");
            continue;
        }

        printf("Received packet from %s:%d\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

        // Directly forward the packet
        forward_packet(buffer, bytes_received, "ens5", "172.23.0.13", multicast_ip, port);
    }

    close(udp_socket);
    return NULL;
}

void start_listening_thread(char *multicast_ip) {
    pthread_t thread;
    if (pthread_create(&thread, NULL, listen_udp_multicast, (void *)multicast_ip) != 0) {
        perror("pthread_create");
    } else {
        pthread_detach(thread);
    }
}

void packet_callback(char *packet, int len) {
    // Placeholder for packet processing if needed
}

void monitor_multicast_traffic() {
    printf("Starting multicast traffic monitoring\n");

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
        sleep(1);
    }
}

int main(int argc, char *argv[]) {
    monitor_multicast_traffic();

    return 0;
}
