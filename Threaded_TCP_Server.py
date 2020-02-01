import sys
import socket
import threading
import socketserver
import time, functools
import _thread
import json
import re
from multiprocessing import Queue
import traceback

CONFIG = dict()

STOP_SERVER = threading.Event()



class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """Request handler"""
    def __init__(self, *args, **kwargs):
        socketserver.BaseRequestHandler.__init__(self, *args, **kwargs)

    def setup(self):
        self.config = CONFIG

    def handle(self):
        '''
            Do your funcky things here !!!
        '''
        try:
            while True:
                data = self.request.recv(1024)
                self.request.send(data)
                print('!!! Data Recieved & Sent :- {}'.format(data.decode()))
                print('@ Time taken to execute the request :- {}'.format(time.time() - self.time_of_request_arrival))
        except KeyboardInterrupt:
            print('Connection Interupted By Client.')
        except Exception as e:
            # print( "EXCEPTION TRACE  PRINT:\n{}".format(traceback.format_exc(e)))
            print('EXCEPTION :- {}'.format(e))
            pass


class Extended_ThreadingMixIN(socketserver.ThreadingMixIn):
    '''
    Extended base class to overide the method which calls the user written function 
    ThreadedTCPRequestHandler(), to add the time parameter
    '''
    def process_request_thread(self, request, client_address):
        self.RequestHandlerClass.time_of_request_arrival = self.time_of_request_arrival
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)


#Extended ThreadingMixIn ::::::::::::::::::::::
class ThreadPoolMixIn(socketserver.ThreadingMixIn):
    '''
    use a thread pool instead of a new thread on every request
    '''
    allow_reuse_address = True  # seems to fix socket.error on server restart
    def serve_forever(self):
        '''
        Handle one request at a time until doomsday.
        '''
        print('[X] Server is Running with No of Threads :- {}'.format(self.numThreads))
        # set up the threadpool
        self.requests = Queue(self.numThreads)
        for x in range(self.numThreads):
            t = threading.Thread(target = self.process_request_thread)
            t.setDaemon(1)
            t.start()

        # server main loop
        while True:
            self.handle_request()
        self.server_close()
    


    def process_request_thread(self):
        '''
        obtain request from queue instead of directly from server socket
        '''
        while True:
            Extended_ThreadingMixIN.process_request_thread(self, *self.requests.get())
    def handle_request(self):
        '''
        simply collect requests and put them on the queue for the workers.
        '''
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            self.time_of_request_arrival = time.time()
            self.requests.put((request, client_address))

class ThreadedTCPServer(ThreadPoolMixIn, socketserver.TCPServer):
    #Extend base class and overide the thread paramter to control the number of threads.
    def __init__(self, no_of_socket_threads, server_address, ThreadedTCPRequestHandler):
        self.numThreads = no_of_socket_threads
        super().__init__(server_address, ThreadedTCPRequestHandler)

def create_multi_threaded_socket(CONFIG, HandlerClass = ThreadedTCPRequestHandler,
        ServerClass = ThreadedTCPServer, 
        protocol="HTTP/1.0"):

    
    server_address = ('', CONFIG['port'])
    HandlerClass.protocol_version = protocol
    server = ThreadedTCPServer(CONFIG['no_of_socket_threads'], server_address, ThreadedTCPRequestHandler)
    sa = server.socket.getsockname()
    print("Serving HTTP on {} port : {}".format(sa[0], sa[1]))
    server.serve_forever()


def main():
    global CONFIG
    CONFIG = { "port" : 10001, "no_of_socket_threads" : 5 }
    create_multi_threaded_socket(CONFIG)

if __name__ == '__main__':
    main()



