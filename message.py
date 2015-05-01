__author__ = 'Haim'
import jsonpickle


class Message(object):
    def __init__(self, user, message, time):
        self.user_name = user.user_name
        self.user_id = user.user_id
        self.message = message
        # self.time = time

    def to_jason(self):
        return jsonpickle.encode(self)

    def to_message(self, mess):
        return jsonpickle.decode(mess)