# Server side

import sys
from socket import socket, AF_INET, SOCK_DGRAM


# User class represents a chat user.
class User:
    def __init__(self, socket_info, name):
        self.ip = socket_info[0]
        self.port = socket_info[1]
        self.name = name
        self.pending_messages = []  # A list of the unread messages of the user.
    
    def get_name(self):
        return self.name

    def get_ip(self):
        return self.ip

    def get_port(self):
        return self.port
    
    # Set a new name to the user.
    def change_user_name(self, new_name):
        self.name = new_name

    # Add a new message to the pending messages of the user.
    def add_new_message(self, message):
        self.pending_messages.append(message)

    # Send the user a concatenation of all his pending messages over the socket.
    def pull_out_messages(self, s):
        concatenated_messages = ""
        # If there are no pending messages - send an empty string.
        if len(self.pending_messages) == 0:
            s.sendto(concatenated_messages, (self.ip, self.port))
            return
        # Concatenate all the messages of the user.
        for i in range(len(self.pending_messages) -1):
            concatenated_messages += self.pending_messages[i]
            concatenated_messages += "\n"
        concatenated_messages += self.pending_messages[len(self.pending_messages) -1]
        # Send the concatenated messages to the user over the socket.
        s.sendto(concatenated_messages, (self.ip, self.port))
        self.pending_messages = []  # Empty the pending messages list.


# Find a specific user and return his index in the list.
# If the user is not in the list - return -1.
def find_user(sender_info, users_list):
    for i in range(len(users_list)):
        if sender_info[0] == users_list[i].get_ip() and sender_info[1] == users_list[i].get_port():
            return i
    return -1


# Format validity check for insert_user, send_message, and change_name requests.
def format_validity_check_first_type(data, s, sender_info):
    # Invalid request format.
    if len(data) == 1 or data[1] != ' ' or len(data) == 2:
        s.sendto("Illegal request" ,sender_info)


# Format validity check for remove_user and get_messages requests.
def format_validity_check_second_type(data, s, sender_info):
    # Invalid request format.
	 if(len(data) != 1):
        s.sendto("Illegal request" ,sender_info)

		
# Insert a new user to the group chat.
def insert_user(s, data, sender_info, users_list):
    # A concatenation of all the users in the group chat.
    users_in_group = ""
    # Check the validity of the request format.
    format_validity_check_first_type(data, s, sender_info)
    # If the user is not registered to the group chat, it is an illegal request.
    if find_user(sender_info, users_list) != -1:
        s.sendto("Illegal request" ,sender_info)
        return
    name = data[2:]  # The name of the new user.
    # Add the new user to the users list.
    users_list.append(User(sender_info, name))
    # Inform the other users that a new user has joined.
    for i in range(len(users_list) - 1):
        users_list[i].add_new_message(name + " has joined")
        users_in_group += users_list[i].get_name()
        if i != len(users_list) - 2:
            users_in_group += ","
    s.sendto(users_in_group, sender_info)


# Send a message to the other group chat users.
def send_message(s, data, sender_info, users_list):
    # Check the validity of the request format.
    format_validity_check_first_type(data, s, sender_info)
    message = data[2:]
    # Find the position of the user in the users list.
    index = find_user(sender_info, users_list)
    # If the user is not registered to the group chat, it is an illegal request.
    if index == -1:
        s.sendto("Illegal request" ,sender_info)
        return
    name_of_sender = users_list[index].get_name()
    # Send the message to the other users.
    for i in range(len(users_list)):
        if i == index:
            continue
        else:
            users_list[i].add_new_message(name_of_sender + ": " + message)
    # When a user sends a message, he gets all his pending messages.
    users_list[index].pull_out_messages(s)


def change_name(s, data, sender_info, users_list):
    # Check the validity of the request format.
    format_validity_check_first_type(data, s, sender_info)
    # The new name of the user.
    new_name = data[2:]
    # Find the position of the user in the users list.
    index = find_user(sender_info, users_list)
    # If the user is not registered to the group chat, it is an illegal request.
    if index == -1:
        s.sendto("Illegal request" ,sender_info)
        return
    # Save the old name of the user that changes his name.
    old_name = users_list[index].get_name()
    users_list[index].change_user_name(new_name)
    # Inform the other users that this user has changed his name.
    for i in range(len(users_list)):
        if i == index:
            continue
        else:
            users_list[i].add_new_message(old_name + " changed his name to " + new_name)
    # When a user changes his name, he gets all his pending messages.
    users_list[index].pull_out_messages(s)


# Remove a user from the group chat.
def remove_user(s, data, sender_info, users_list):
    # Check the validity of the request format.
    format_validity_check_second_type(data, s, sender_info)
    index = find_user(sender_info, users_list)
    # If the user is not registered to the group chat, it is an illegal request.
    if index == -1:
        s.sendto("Illegal request" ,sender_info)
        return
    # Save the user's name and remove him from the user list.
    name = users_list[index].get_name()
    users_list.pop(index)
    # Inform the other users that this user has left the group chat.
    for i in range(len(users_list)):
        users_list[i].add_new_message(name + " has left the group")
    s.sendto("" ,sender_info)


# Send the user all his pending messages over the socket.
def get_messages(s, data, sender_info, users_list):
    # Check the validity of the request format.
    format_validity_check_second_type(data, s, sender_info)
    index = find_user(sender_info, users_list)
    # If the user is not registered to the group chat, it is an illegal request.
    if index == -1:
        s.sendto("Illegal request" ,sender_info)
        return
    users_list[index].pull_out_messages(s)


# Analyze the request of the client and handle it.
def analyze_data(s, data, sender_info, users_list):
    # An empty request.
    if len(data) == 0:
        s.sendto("Illegal request" ,sender_info)
        return
    first_char = data[0]
    if first_char == '1':
        # Insert a new user to the group chat.
        insert_user(s, data, sender_info, users_list)
    elif first_char == '2':
        # Send a message to the other group chat users.
        send_message(s, data, sender_info, users_list)
    elif first_char == '3':
        # Change the name of the user.
        change_name(s, data, sender_info, users_list)
    elif first_char == '4':
        # Remove a user from the group chat.
        remove_user(s, data, sender_info, users_list)
    elif first_char == '5':
        # Get all the pending messages.
        get_messages(s, data, sender_info, users_list)
    else:
        # Invalid request format.
        s.sendto("Illegal request" ,sender_info)


def main():
    # The first argument to main is the source port of the server.
    source_port = int(sys.argv[1])
    source_ip = '0.0.0.0'
    # Create a UDP socket.
    s = socket(AF_INET, SOCK_DGRAM)
    # Bind the socket to the IP & port of the server.
    s.bind((source_ip, source_port))
    # A list of the existing users in the group chat.
    users_list = []
    while True:
        # Handle a request of a client.
        data, sender_info = s.recvfrom(2048)
        # Analyze the request.
        analyze_data(s, data, sender_info, users_list)


if __name__ == "__main__":
    main()
