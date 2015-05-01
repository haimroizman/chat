__author__ = 'Haim'

import re
from DB.chat_repository import ChatUserRepository, ChatMessageRepository
from time import gmtime, strftime


class UserService:
    def __init__(self, user_name, user_socket):
        self.user_name = user_name
        self.user_id = None
        self.chat_user_repository = ChatUserRepository()
        self.chat_message_repository = ChatMessageRepository()
        self.user_socket = user_socket

    def validate_user(self):
        if len(self.user_name) < 6 or len(self.user_name) > 12:
            return False

        match_user_name = re.match(r'^[A-Z a-z]+[0-9]+$', self.user_name, re.M | re.I)
        if match_user_name:
            return True

        return False

    def check_existence_update_user_id(self):
        user_generator = self.chat_user_repository.read_user_execute(self.user_name)
        for row in user_generator:
            self.user_id = list(row)[0]
            self.user_socket.send('From user_service:user_is: %s ' % self.user_id)
            return
        self.add_new_user()
        self.check_existence_update_user_id()

    def add_new_user(self):
        user_value = {'user_name': self.user_name}
        self.chat_user_repository.insert_user_execute(**user_value)

    def add_users_message(self, user_quote):
        message_values = {'message_col': user_quote, 'user_id': self.user_id,
                          'send_date': strftime("%Y-%m-%d", gmtime())}
        self.chat_message_repository.insert_message_execute(**message_values)

    def display_users_last_messages(self):
        message_row_generator = self.chat_message_repository.read_message_execute(5)
        for message in message_row_generator:
            self.user_socket.send(message[1])



