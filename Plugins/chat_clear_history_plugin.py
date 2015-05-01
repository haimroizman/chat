from IChatTask import IChatTask
from log_manager import LogManager
from DB.chat_repository import ChatMessageRepository

__author__ = 'Haim'


class ChatClearHistoryPlugin(IChatTask):
    def __init__(self):
        self.logger = LogManager("chatApp")
        self.chat_message_repository = ChatMessageRepository()

    def execute_task(self, under_num_days):
        self.logger.debug_log('The clear history task should start soon')
        self.chat_message_repository.delete_previous_message_execute(under_num_days)
