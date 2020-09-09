# Client side

import sys
from socket import socket, AF_INET, SOCK_DGRAM


def main():
    # The first argument to main is the dest IP of the client (the source IP of the sever).
    dest_ip = sys.argv[1]
    # The second argument to main is the dest port of the client (the source port of the sever).
    dest_port = int(sys.argv[2])
    s = socket(AF_INET, SOCK_DGRAM)  # Create a UDP socket.
    # The size of the buffer for receiving data from the socket.
    buffer_size = 2048
    while True:
        msg = raw_input()  # Get a request from the user.
        s.sendto(msg, (dest_ip,dest_port))  # Send the request to the server.
        # The response of the server to the request.
        data, sender_info = s.recvfrom(buffer_size)
        # If the response is not an empty string - print it to the screen.
        if data != "":
            print data
    s.close()  # Close the socket.


if __name__ == "__main__":
    main()
