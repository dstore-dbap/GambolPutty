# -*- coding: utf-8 -*-
import logging
import threading
import SocketServer
import ssl
import sys
import socket
import Queue
import Utils
import BaseModule
from Decorators import ModuleDocstringParser

class ThreadPoolMixIn(SocketServer.ThreadingMixIn):
    """
    Use a thread pool instead of a new thread on every request.

    Using a threadpool prevents the spawning of a new thread for each incoming
    request. This should increase performance a bit.

    See: http://code.activestate.com/recipes/574454/
    """
    numThreads = 15
    allow_reuse_address = True  # seems to fix socket.error on server restart
    is_alive = True

    def serve_forever(self):
        """
        Handle one request at a time until doomsday.
        """
        # Set up the threadpool.
        self.requests = Queue.Queue(self.numThreads)

        for x in range(self.numThreads):
            t = threading.Thread(target=self.process_request_thread)
            t.setDaemon(1)
            t.start()

        # server main loop
        while self.is_alive:
            self.handle_request()

        self.server_close()


    def process_request_thread(self):
        """
        obtain request from queue instead of directly from server socket
        """
        while True:
            SocketServer.ThreadingMixIn.process_request_thread(self, *self.requests.get())


    def handle_request(self):
        """
        simply collect requests and put them on the queue for the workers.
        """
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            self.requests.put((request, client_address))


class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):
    def __init__(self, tcp_server_instance, *args, **keys):
        self.tcp_server_instance = tcp_server_instance
        self.logger = logging.getLogger(self.__class__.__name__)
        SocketServer.BaseRequestHandler.__init__(self, *args, **keys)

    def handle(self):
        try:
            host, port = self.request.getpeername()
            data = True
            while data:
                data = self.rfile.readline().strip()
                if data == "":
                    continue
                self.tcp_server_instance.addEventToOutputQueues(Utils.getDefaultDataDict({"received_from": host, "data": data}))
        except socket.timeout, e:
            # Handle a timeout gracefully
            self.finish()


class ThreadedTCPServer(ThreadPoolMixIn, SocketServer.TCPServer):

    allow_reuse_address = True

    def __init__(self, *args, **kwargs):
        self.use_tls = kwargs['tls'] if 'tls' in kwargs else False
        self.cert_file = kwargs['cert'] if 'cert' in kwargs else False
        SocketServer.TCPServer.__init__(self, *args)

    def server_bind(self):
        SocketServer.TCPServer.server_bind(self)
        if(self.use_tls):
            self.socket = ssl.wrap_socket(self.socket, server_side=True, certfile=self.cert_file, do_handshake_on_connect=False)

    def get_request(self):
        (socket, addr) = SocketServer.TCPServer.get_request(self)
        socket.do_handshake()
        return (socket, addr)

class TCPRequestHandlerFactory:
    def produce(self, tcp_server_instance):
        def createHandler(*args, **keys):
            return ThreadedTCPRequestHandler(tcp_server_instance, *args, **keys)
        return createHandler

@ModuleDocstringParser
class TcpServerThreaded(BaseModule.BaseModule):
    """
    Reads data from tcp socket and sends it to its output queues.

    Configuration example:

    - module: TcpServerThreaded
      configuration:
        interface: localhost             # <default: 'localhost'; type: string; is: optional>
        port: 5151                       # <default: 5151; type: integer; is: optional>
        tls: False                       # <default: False; type: boolean; is: optional>
        cert: /path/to/cert.pem          # <default: False; type: boolean||string; is: optional>
      receivers:
        - NextModule
    """

    module_type = "input"
    """Set module type"""

    def configure(self, configuration):
        # Call parent configure method
        BaseModule.BaseModule.configure(self, configuration)
        self.server = False

    def run(self):
        if not self.output_queues:
            self.logger.warning("Will not start module %s since no output queue set." % (self.__class__.__name__))
            return
        handler_factory = TCPRequestHandlerFactory()
        try:
            self.server = ThreadedTCPServer((self.getConfigurationValue("interface"),
                                             self.getConfigurationValue("port")),
                                             handler_factory.produce(self),
                                             tls=self.getConfigurationValue("tls"),
                                             cert=self.getConfigurationValue("cert"))
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("Could not listen on %s:%s. Exception: %s, Error: %s" % (self.getConfigurationValue("interface"),
                                                                                       self.getConfigurationValue("port"), etype, evalue))
            self.gp.shutDown()
            return
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.server_thread.daemon = True
        self.server_thread.start()

    def shutDown(self):
        if self.server:
            self.server.server_close()
            self.server.is_alive = False