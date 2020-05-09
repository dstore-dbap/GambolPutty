# -*- coding: utf-8 -*-
import sys
import os
import yaml
import logging
import logging.config
import threading
import unittest
import mock
import queue
import unittest


sys.path.append('../')

import tests.ServiceDiscovery
from lumbermill.constants import LOGLEVEL_STRING_TO_LOGLEVEL_INT, LUMBERMILL_BASEPATH
from lumbermill.utils.ConfigurationValidator import ConfigurationValidator
from lumbermill.utils.misc import AnsiColors, coloredConsoleLogging
from lumbermill.utils.MultiProcessDataStore import MultiProcessDataStore

class StoppableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

class MockLumberMill(mock.Mock):

    def __init__(self):
        mock.Mock.__init__(self)
        self.modules = {}
        self.internal_datastore = MultiProcessDataStore()
        self.worker_count = 1
        self.is_master_process = True

    def is_master(self):
        return self.is_master_process

    def getModuleInfoById(self, module_id, silent=True):
        try:
            return self.modules[module_id]
        except KeyError:
            if not silent:
                self.logger.error("Get module by id %s failed. No such module." % module_id)
            return None

    def getMainProcessId(self):
        return os.getpid()

    def setWorkerCount(self, count):
        self.worker_count = count

    def getWorkerCount(self):
        return self.worker_count

    def getInternalDataStore(self):
        return self.internal_datastore;

    def setInInternalDataStore(self, key, value):
        self.internal_datastore.setValue(key, value)

    def getFromInternalDataStore(self, key, default=None):
        try:
            return self.internal_datastore.getValue(key)
        except KeyError:
            return default

    def initModule(self, module_name):
        instance = None
        try:
            module = __import__(module_name)
            module_class = getattr(module, module_name)
            instance = module_class(self)
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not init module %s. Exception: %s, Error: %s." % (module_name, etype, evalue))
        return instance

    def addModule(self, module_name, module_instances):
        if module_name in self.modules:
            return
        if not type(module_instances) is list:
            module_instances = [module_instances]
        self.modules[module_name] = {'idx': len(self.modules),
                                     'instances': module_instances,
                                     'type': module_instances[0].module_type,
                                     'configuration': module_instances[0].configuration_data}

    def shutDown(self):
        for module_name, mod in self.modules.iteritems():
            mod.shutDown()

class MockReceiver(mock.Mock):

    def __init__(self):
        mock.Mock.__init__(self)
        self.events = []
        self.filter = False

    def setFilter(self, filter):
        self.filter = filter

    def getFilter(self):
        return self.filter

    def receiveEvent(self, event):
        self.handleEvent(event)
        return event

    def handleEvent(self, event):
        self.events.append(event)

    def getEvent(self):
        for event in self.events:
            yield event

    def hasEvents(self):
        return True if len(self.events) > 0 else False

class ModuleBaseTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ModuleBaseTestCase, self).__init__(*args, **kwargs)
        self.path_to_config_file = ("%s/../tests/conf/unittest.conf" % LUMBERMILL_BASEPATH)
        self.configuration = {'logging': {'level': 'info',
                                          'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                          'filename': None,
                                          'filemode': 'w'}}
        logging.basicConfig(handlers=logging.StreamHandler())
        self.logger = logging.getLogger(self.__class__.__name__)
        self.configure()
        self.configureLogging()
        self.conf_validator = ConfigurationValidator()
        self.receiver = MockReceiver()

    def configure(self):
        """Loads and parses the configuration"""
        try:
            with open(self.path_to_config_file, "r") as configuration_file:
                self.raw_conf_file = configuration_file.read()
            configuration = yaml.load(self.raw_conf_file, Loader=yaml.FullLoader)
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not read config file %s. Exception: %s, Error: %s." % (self.path_to_config_file, etype, evalue))
            sys.exit()
        self.configuration.update(configuration)

    def configureLogging(self):
        # Logger configuration.
        if self.configuration['logging']['level'].lower() not in LOGLEVEL_STRING_TO_LOGLEVEL_INT:
            print("Loglevel unknown.")
            sys.exit(255)
        log_level = LOGLEVEL_STRING_TO_LOGLEVEL_INT[self.configuration['logging']['level'].lower()]
        logging.basicConfig(level=log_level,
                            format=self.configuration['logging']['format'],
                            filename=self.configuration['logging']['filename'],
                            filemode=self.configuration['logging']['filemode'])
        if not self.configuration['logging']['filename']:
            logging.StreamHandler.emit = coloredConsoleLogging(logging.StreamHandler.emit)

    def setUp(self, test_object):
        test_object.addReceiver('MockReceiver', self.receiver)
        self.test_object = test_object
        if hasattr(test_object, 'setInputQueue'):
            self.input_queue = queue.Queue()
            self.test_object.setInputQueue(self.input_queue)

    def checkConfiguration(self):
        result = self.conf_validator.validateModuleConfiguration(self.test_object)
        self.assertFalse(result)

    def startTornadoEventLoop(self):
        import tornado.ioloop
        self.ioloop_thread = threading.Thread(target=tornado.ioloop.IOLoop.instance().start)
        self.ioloop_thread.daemon = True
        self.ioloop_thread.start()

    def stopTornadoEventLoop(self):
        if not hasattr(self, 'ioloop_thread'):
            return
        import tornado.ioloop
        tornado.ioloop.IOLoop.instance().stop()
        self.ioloop_thread.stop()
        self.ioloop_thread = None

    def getRedisService(self):
        service = tests.ServiceDiscovery.discover_redis()
        if service:
            return service
        return {'server': self.configuration['redis']['server'],
                'port': self.configuration['redis']['port']}

    def getElasticSeachService(self):
        service = tests.ServiceDiscovery.discover_elasticsearch()
        if service:
            return service
        return {'server': self.configuration['elasticsearch']['server'],
                'port': self.configuration['elasticsearch']['port']}

    def getMongoDBService(self):
        service = tests.ServiceDiscovery.discover_mongodb()
        if service:
            return service
        return {'server': self.configuration['mongodb']['server'],
                'port': self.configuration['mongodb']['port']}

    """
    @unittest.skip("Skipping test. Feature removed.")
    def testQueueCommunication(self, config = {}):
        output_queue = queue.Queue()
        self.test_object.configure(config)
        if hasattr(self.test_object, 'start'):
            self.test_object.start()
        else:
            self.test_object.run()
        self.input_queue.put(getDefaultEventDict({}))
        queue_emtpy = False
        try:
            output_queue.get(timeout=2)
        except queue.Empty:
            queue_emtpy = True
        self.assert_(queue_emtpy != True)

    @unittest.skip("Skipping test. Feature removed.")
    def testWorksOnOriginal(self, config = {}):
        output_queue = queue.Queue()
        config['work_on_copy'] = {'value': False, 'contains_dynamic_value': False}
        data_dict = getDefaultEventDict({})
        self.test_object.configure(config)
        self.test_object.start()
        self.input_queue.put(data_dict)
        queue_emtpy = False
        try:
            returned_data_dict = output_queue.get(timeout=1)
        except queue.Empty:
            queue_emtpy = True
        self.assert_(queue_emtpy == False and returned_data_dict is data_dict)

    @unittest.skip("Skipping test. Feature removed.")
    def testWorksOnCopy(self, config = {}):
        output_queue = queue.Queue()
        config['work_on_copy'] = {'value': True, 'contains_dynamic_value': False}
        data_dict = getDefaultEventDict({})
        self.test_object.configure(config)
        self.test_object.start()
        self.input_queue.put(data_dict)
        queue_emtpy = False
        try:
            returned_data_dict = output_queue.get(timeout=1)
        except queue.Empty:
            queue_emtpy = True
        self.assert_(queue_emtpy == False and returned_data_dict is not data_dict)

    @unittest.skip("Skipping test. Feature removed.")
    def testOutputQueueFilterNoMatch(self, config = {}):
        output_queue = queue.Queue()
        data_dict = getDefaultEventDict({})
        data_dict['Johann'] = 'Gambolputty'
        result = self.test_object.configure(config)
        self.assertFalse(result)
        self.test_object.addOutputQueue(output_queue, filter='Johann == "Gambolputty de von ausfern" or Johann != "Gambolputty"')
        self.test_object.start()
        self.input_queue.put(data_dict)
        queue_emtpy = False
        returned_data_dict = {}
        try:
            returned_data_dict = output_queue.get(timeout=2)
        except queue.Empty:
            queue_emtpy = True
        self.assert_(queue_emtpy == True)

    @unittest.skip("Skipping test. Feature removed.")
    def testOutputQueueFilterMatch(self,config = {}):
        output_queue = queue.Queue()
        data_dict = getDefaultEventDict({'Johann': 'Gambolputty', 'event_type': 'agora_access_log'})
        result = self.test_object.configure(config)
        self.assertFalse(result)
        self.test_object.addOutputQueue(output_queue, filter='Johann in ["Gambolputty", "Blagr"] or Johan not in ["Gambolputty", "Blagr"]')
        self.test_object.start()
        self.input_queue.put(data_dict)
        queue_emtpy = False
        returned_data_dict = {}
        try:
            returned_data_dict = output_queue.get(timeout=2)
        except queue.Empty:
            queue_emtpy = True
        print(data_dict)
        print(returned_data_dict)
        self.assert_(queue_emtpy == False and 'Johann' in returned_data_dict)
    """

    def tearDown(self):
        self.stopTornadoEventLoop()
        self.test_object.shutDown()
