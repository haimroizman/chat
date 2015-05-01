__author__ = 'Haim'

from messages_producer_consumer import TCPServer, TCPProducerClient
import select
from log_manager import LogManager
from plugin_tasks_server import PluginTaskServer

# TODO: Replace all the print functions with logs.

def event_loop(handlers):
    logger.info_log('The server starts to serve-> event_loop')
    while True:
        wants_recv = [h for h in handlers if h.wants_to_receive()]
        wants_send = [h for h in handlers if h.wants_to_send()]

        can_recv, can_send, _ = select.select(wants_recv, wants_send, [])

        for h in can_recv:
            h.handle_receive()

        for h in can_send:
            h.handle_send()


if __name__ == '__main__':
    plugin_tasks_server = PluginTaskServer()
    plugin_tasks_server.start()

    handlers = []
    logger = LogManager("chatApp")
    handlers.append(TCPServer(('', 6001), TCPProducerClient, handlers))
    event_loop(handlers)