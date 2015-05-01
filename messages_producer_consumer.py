__author__ = 'Haim'

from socket import *
import Queue
import concurrent.futures
from log_manager import LogManager
import multiprocessing
from threading import Thread
from user_service import UserService

max_conn_pool = multiprocessing.cpu_count()

logger = LogManager("chatApp")


class EventHandler:
    def fileno(self):
        # 'Return the associated file descriptor'
        raise NotImplemented('must implement')

    def wants_to_receive(self):
        # 'Return True if receiving is allowed'
        return False

    def handle_receive(self):
        # 'Perform the receive operation'
        pass

    def wants_to_send(self):
        # 'Return True if sending is requested'
        return False

    def handle_send(self):
        # 'Send outgoing data'
        pass

    def get_personal_queue(self):
        return None


class TCPServer(EventHandler):
    def __init__(self, address, client_handler, handler_list):
        self.client_handler = client_handler
        self.handler_list = handler_list

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, True)

        self.sock.bind(address)
        self.sock.listen(10)

    def fileno(self):
        return self.sock.fileno()

    def wants_to_receive(self):
        return True

    def handle_receive(self):
        client, addr = self.sock.accept()
        logger.info_log('received client socket fd:%s' % client.fileno())
        try:
            client.send('Login : Please enter your user name and press enter: ')
        except Exception, e:
            logger.exception_log('Broken socket connection with fd: %s and the following error message: %s' \
                                 % (client.fileno(), str(e)))
            client.close()
        user_service = UserService(None, client)
        # Add the client to the event loop's handler list
        self.handler_list.append(self.client_handler(user_service, self.handler_list))


class TCPConsumerClient(EventHandler):
    def __init__(self, user_service, handler_list):
        self.user_service = user_service
        self.sock = self.user_service.user_socket
        self.handler_list = handler_list
        self.personal_queue = Queue.Queue()
        self.file_number = self.sock.fileno()


    def get_personal_queue(self):
        return self.personal_queue

    def fileno(self):
        return self.file_number

    def close(self):
        self.sock.close()
        # Remove myself from the event loop's handler list
        self.handler_list.remove(self)

    def wants_to_send(self):
        return True if not self.personal_queue.empty() else False  # self.outgoing else False

    def handle_send(self):
        next_msg = None
        try:
            if not self.personal_queue.empty():
                next_msg = self.personal_queue.get_nowait()
        except Queue.Empty, error:
            # No messages waiting so stop checking for writability.
            logger.error_log('output queue for', self.sock.getpeername(), 'is empty')
            logger.exception_log("Error!")
            self.close()

        if next_msg is not None:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_conn_pool) as executor:
                # TODO: Don't forget to start using message objects-> so ill be able to send nick_name, message and peer
                for handler in self.handler_list:
                    # Do not send the message to the client who has send us the message
                    if handler.get_personal_queue() is not None and handler.sock != self.sock and \
                            handler.user_service.user_id:
                        mess = "\r" + '<' + str(self.sock.getpeername()).rstrip('\n') + '> ' + next_msg
                        logger.info_log('going to be send to fd : %s' % handler.sock.fileno())
                        broadcast = BroadCastingService(handler.sock, mess)
                        executor.submit(broadcast.broadcast_messages)


class TCPProducerClient(TCPConsumerClient):
    def wants_to_receive(self):
        return True

    def handle_receive(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as execute:
            receive = ReceivingService(self.user_service, self.personal_queue, self.handler_list, self)
            execute.submit(receive.receive_message)


class BroadCastingService:
    def __init__(self, conn, mess):
        self.sock_conn = conn
        self.message = mess

    def broadcast_messages(self):
        try:
            self.sock_conn.send(self.message)
        except Exception, e:
            logger.exception_log('Broken socket connection with fd: %s and the following error message: %s' \
                                 % (self.sock_conn.fileno(), str(e)))
            self.sock_conn.close()


class ReceivingService:
    def __init__(self, user_service, queue, handler_list, self_to_remove):
        self.user_service = user_service
        self.sock_conn = self.user_service.user_socket
        self.data = None
        self.queue = queue
        self.self_to_remove = self_to_remove
        self.handler_list = handler_list

    def receive_message(self):
        try:
            self.data = self.sock_conn.recv(4096)
            if not self.user_service.user_id and self.data:
                self.login_procedure()
            else:
                self.data = self.user_service.user_name.rstrip('\n') + ':' + self.data
                self.user_service.add_users_message(self.data)
        except Exception as error:
            logger.exception_log(error.message)
            self.sock_conn.close()
            self.handler_list.remove(self.self_to_remove)

        else:
            if not self.data:
                self.sock_conn.close()
            else:
                logger.info_log('received %s from %s' % (self.data, self.sock_conn.fileno()))
                self.queue.put(self.data)


    def login_procedure(self):
        attempts_num = 0
        while attempts_num < 5 and not self.user_service.user_id:
            self.user_service.user_name = self.data
            if self.user_service.validate_user():
                self.user_service.check_existence_update_user_id()
                self.sock_conn.send('You can start typing....\n')
                self.data += self.data.rstrip('\n') + ' has entered the room.....'
                last_history_messages_thread = Thread(target=self.display_last_messages)
                last_history_messages_thread.start()
                return True

            self.sock_conn.send(
                'Enter valid user_name. It has to be between 6-12 characters, '
                'it must start with letters and end with numbers: ')
            self.data = self.sock_conn.recv(4096)
            continue

    def display_last_messages(self):
        self.user_service.display_users_last_messages()