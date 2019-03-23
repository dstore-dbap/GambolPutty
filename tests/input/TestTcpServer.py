import sys
import time
import mock
import socket
import ssl
import lumbermill.utils.DictUtils as DictUtils

from lumbermill.constants import LUMBERMILL_BASEPATH
from tests.ModuleBaseTestCase import ModuleBaseTestCase
from lumbermill.input import TcpServer


class TestTcpServer(ModuleBaseTestCase):

    def setUp(self):
        super(TestTcpServer, self).setUp(TcpServer.TcpServer(mock.Mock()))

    def TestATcpConnection(self):
        print("testTcpConnection")
        self.test_object.configure({'port': 5353,
                                    'simple_separator': '\n'})
        self.checkConfiguration()
        self.test_object.initAfterFork()
        self.startTornadoEventLoop()
        # Give server process time to startup.
        time.sleep(.1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(('localhost', self.test_object.getConfigurationValue('port')))
            for _ in range(0, 1500):
                s.sendall("Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.\n")
            s.shutdown(socket.SHUT_RDWR)
            s.close()
            connection_succeeded = True
        except:
            etype, evalue, etb = sys.exc_info()
            print "Could not connect to %s:%s. Exception: %s, Error: %s" % ('localhost', self.test_object.getConfigurationValue("port"), etype, evalue)
            connection_succeeded = False
        self.assertTrue(connection_succeeded)
        expected_ret_val = DictUtils.getDefaultEventDict({'data': "Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever."})
        expected_ret_val.pop('lumbermill')
        event = False
        time.sleep(2)
        counter = 0
        for event in self.receiver.getEvent():
            counter += 1
        self.assertTrue(event is not False)
        self.assertEqual(counter, 1500)
        event.pop('lumbermill')
        self.assertDictEqual(event, expected_ret_val)
        self.tearDown()

    def testATlsTcpConnection(self):
        self.test_object.configure({'port': 5252,
                                    'tls': True,
                                    'key': LUMBERMILL_BASEPATH + '/../tests/test_data/gambolputty_ca.key',
                                    'cert': LUMBERMILL_BASEPATH + '/../tests/test_data/gambolputty_ca.crt',
                                    'timeout': 1})
        self.checkConfiguration()
        self.test_object.initAfterFork()
        self.startTornadoEventLoop()
        # Give server process time to startup.
        time.sleep(1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
            s.connect((self.test_object.getConfigurationValue('interface'), self.test_object.getConfigurationValue('port')))
            for _ in range(0, 1500):
                s.sendall("Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.\n")
            s.close()
            connection_succeeded = True
        except:
            etype, evalue, etb = sys.exc_info()
            print "Could not connect to %s:%s. Exception: %s, Error: %s" % ( self.test_object.getConfigurationValue("interface"),
                                                                            self.test_object.getConfigurationValue("port"), etype, evalue)
            connection_succeeded = False
        self.assertTrue(connection_succeeded)
        expected_ret_val =  DictUtils.getDefaultEventDict({'data': "Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever."})
        expected_ret_val.pop('lumbermill')
        event = False
        time.sleep(2)
        counter = 0
        for event in self.receiver.getEvent():
            counter += 1
        self.assertTrue(event != False)
        self.assertEqual(counter, 1500)
        event.pop('lumbermill')
        self.assertDictEqual(event, expected_ret_val)
        self.tearDown()

    def testLineModeRegexSeparator(self):
        self.test_object.configure({'regex_separator': 'C[oO]nfused?\s+ca+t'})
        self.checkConfiguration()
        self.test_object.initAfterFork()
        self.startTornadoEventLoop()
        # Give server process time to startup.
        time.sleep(.1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(('localhost', self.test_object.getConfigurationValue('port')))
            s.sendall("Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.Confused catBeethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.COnfuse cat")
            s.sendall("Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.Confused caaatBeethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.Confused   cat")
            s.close()
            connection_succeeded = True
        except:
            etype, evalue, etb = sys.exc_info()
            print "Could not connect to %s:%s. Exception: %s, Error: %s" % ( 'localhost', self.test_object.getConfigurationValue("port"), etype, evalue)
            connection_succeeded = False
        self.assertTrue(connection_succeeded)
        event = None
        time.sleep(1)
        counter = 0
        for event in self.receiver.getEvent():
            counter += 1
        self.assertIsNotNone(event)
        self.assertEquals(counter, 4)
        self.assertEquals(event['data'], "Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.Confused   cat")
        self.tearDown()

    def testLineModeSimpleSeparator(self):
        self.test_object.configure({'simple_separator': '***'})
        self.checkConfiguration()
        self.test_object.initAfterFork()
        self.startTornadoEventLoop()
        # Give server process time to startup.
        time.sleep(.1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(('localhost', self.test_object.getConfigurationValue('port')))
            s.sendall("Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.***Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.***")
            s.sendall("Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.***Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.***")
            s.close()
            connection_succeeded = True
        except:
            etype, evalue, etb = sys.exc_info()
            print "Could not connect to %s:%s. Exception: %s, Error: %s" % ( 'localhost', self.test_object.getConfigurationValue("port"), etype, evalue)
            connection_succeeded = False
        self.assertTrue(connection_succeeded)
        event = None
        time.sleep(1)
        counter = 0
        for event in self.receiver.getEvent():
            counter += 1
        self.assertIsNotNone(event)
        self.assertEquals(counter, 4)
        self.assertEquals(event['data'], "Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.***")
        self.tearDown()

    def testStreamMode(self):
        self.test_object.configure({'mode': 'stream',
                                    'chunksize': 1024})
        self.checkConfiguration()
        self.test_object.initAfterFork()
        self.startTornadoEventLoop()
        # Give server process time to startup.
        time.sleep(.1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(('localhost', self.test_object.getConfigurationValue('port')))
            for _ in range(0, 50):
                s.sendall("Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.")
            s.close()
            connection_succeeded = True
        except:
            etype, evalue, etb = sys.exc_info()
            print "Could not connect to %s:%s. Exception: %s, Error: %s" % ('localhost', self.test_object.getConfigurationValue("port"), etype, evalue)
            connection_succeeded = False
        self.assertTrue(connection_succeeded)
        events = []
        time.sleep(1)
        for event in self.receiver.getEvent():
            events.append(event)
        self.assertEquals(len(events), 6)
        self.assertEquals(len(events[0]['data']), 1024)
        self.tearDown()

    def tearDown(self):
        self.test_object.shutDown()
        ModuleBaseTestCase.tearDown(self)