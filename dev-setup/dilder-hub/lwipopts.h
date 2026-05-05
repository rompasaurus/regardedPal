#ifndef _LWIPOPTS_H
#define _LWIPOPTS_H

/* Minimal lwIP config for WiFi + NTP on Pico W / Pico 2 W */

#define NO_SYS                      1
#define LWIP_SOCKET                 0
#define LWIP_NETCONN                0

#define MEM_LIBC_MALLOC             0
#define MEM_ALIGNMENT               4
#define MEM_SIZE                    4000

#define MEMP_NUM_TCP_PCB            4
#define MEMP_NUM_TCP_SEG            16
#define MEMP_NUM_ARP_QUEUE          4
#define MEMP_NUM_NETBUF             2
#define MEMP_NUM_NETCONN            4

#define PBUF_POOL_SIZE              16

#define LWIP_ARP                    1
#define LWIP_ETHERNET               1
#define LWIP_ICMP                   1
#define LWIP_RAW                    1
#define LWIP_TCP                    1
#define LWIP_UDP                    1
#define LWIP_IPV4                   1
#define LWIP_DHCP                   1
#define LWIP_DNS                    1

/* SNTP (NTP client) */
#define LWIP_SNTP                   1
#define SNTP_SERVER_DNS             1
#define SNTP_MAX_SERVERS            2
#define SNTP_SET_SYSTEM_TIME_US(sec, us) sntp_set_system_time_cb(sec, us)

#define LWIP_NETIF_STATUS_CALLBACK  1
#define LWIP_NETIF_LINK_CALLBACK    1

#define TCP_WND                     (4 * TCP_MSS)
#define TCP_MSS                     1460
#define TCP_SND_BUF                 (4 * TCP_MSS)

#define LWIP_CHKSUM_ALGORITHM       3

#define LWIP_HTTPD_CGI              0
#define LWIP_HTTPD_SSI              0

#endif
