from log_manager import LogManager

__author__ = 'Haim'

logger = LogManager("chatApp")
_call_backs = {}


def subscribe_event(event_name, call_back):
    event_call_backs = _call_backs.get(event_name)

    if event_call_backs is not None:
        event_call_backs.append(call_back)
    else:
        _call_backs[event_name] = [call_back]


def publish_event(event_name, kwargs=None):
    for call_back in _call_backs[event_name]:
        try:
            call_back(**kwargs)
        except Exception as e:
            logger.error_log('Error while trying to publish event : %s. Exception : %s' % (event_name, str(e)))


def un_subscribe_event(event_name):
    del _call_backs[event_name]