import socket

# Set up the address and port to receive on
RECEIVER_ADDRESS = 'localhost'
RECEIVER_PORT = 12345

while True:
    # Create a socket object
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the address and port
    receiver_socket.bind((RECEIVER_ADDRESS, RECEIVER_PORT))

    # Listen for incoming connections
    receiver_socket.listen()

    # Accept a connection from a sender
    sender_socket, sender_address = receiver_socket.accept()

    # Receive data from the sender
    received_data = sender_socket.recv(1024)

    # Decode the received data from bytes to string
    decoded_data = received_data.decode('utf-8')

    # Print the received data
    print(f'Received data: {decoded_data}')

    # Close the sender socket and the receiver socket
    sender_socket.close()
    receiver_socket.close()
