__author__ = 'Haim'
import os
import threading
import importlib
import inspect
import IChatTask
import event_aggregator
import hermes.backend.dict
import datetime

last_clear_date = None

cache = hermes.Hermes(hermes.backend.dict.Backend)


@cache
def get_last_clear_date():
    return last_clear_date


class PluginTaskServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.plugin_objects = {}
        self.last_clear_date = None
        self.updated_before = None


    def run(self):
        global last_clear_date
        while True:
            for cache_key, cache_value in cache.backend.dump().items():
                if cache_value is not None:
                    self.updated_before = abs(datetime.datetime.now() - cache_value).days
            if self.updated_before is not None and self.updated_before < 7:
                continue
            self.find_subscribe_plugins()
            event_aggregator.publish_event('ClearHistory', {'under_num_days': 60})
            cache.clean()
            last_clear_date = datetime.datetime.now()
            # Just for updating the caching
            get_last_clear_date()


    def find_subscribe_plugins(self):
        for root, dirs, files in os.walk(os.getcwd()):
            if 'Plugins' in root:
                for module_file in [file_path for file_path in files if file_path.endswith('.py')]:
                    module = importlib.import_module('Plugins.' + module_file[:-3])
                    for plug in [m[1] for m in inspect.getmembers(module) if inspect.isclass(m[1])]:
                        bases = inspect.getmro(plug)
                        if bases[0].__name__ != IChatTask.IChatTask.__name__ and \
                                        IChatTask.IChatTask.__name__ in [i.__name__ for i in bases]:
                            plugin_object = plug()
                            event_aggregator.subscribe_event("ClearHistory", plugin_object.execute_task)
                            if self.plugin_objects.has_key('ClearHistory'):
                                self.plugin_objects['ClearHistory'].append(plugin_object)
                            else:
                                self.plugin_objects['ClearHistory'] = [plugin_object]

