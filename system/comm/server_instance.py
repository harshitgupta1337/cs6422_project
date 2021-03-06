#!/usr/bin/env python

import threading
import zmq
from zmq.devices import ProcessDevice

class Server(object):
    def __init__(self, url, msg_recv_callback):
        self.zmq_context = zmq.Context()
        self.msg_recv_callback = msg_recv_callback
        self.url = url
    
    def start(self):
        
        #Instantiate workers, Accept client connections, distribute computation requests among workers, route computed results back to clients.
        # Front facing socket to accept client connections.
        socket_front = self.zmq_context.socket(zmq.ROUTER)
        print ("Binding to " , self.url)
        socket_front.bind(self.url)
        
        # Backend socket to distribute work.
        socket_back = self.zmq_context.socket(zmq.DEALER)
        socket_back.bind('inproc://backend')
        
        self.worker = Worker(self.zmq_context, self)
        self.worker.start()
        print ("started server socket worker")
        
        # Read a client's socket ID and request. => Send socket ID and request to a worker. => Read a client's socket ID and result from a worker. => Route result back to the client using socket ID.
        zmq.device(zmq.QUEUE, socket_front, socket_back)
        print ("setup zmq device")
        
    def sendMsg(self, client_id, msg):
        self.worker.sendMsg(client_id, msg)

class Worker(threading.Thread):
    
    def __init__(self, zmq_context, parent):
        threading.Thread.__init__(self)
        self.zmq_context = zmq_context
        self.parent = parent
    
    def run(self):
        #Socket to communicate with front facing server.
        self.socket = self.zmq_context.socket(zmq.DEALER)
        self.socket.connect('inproc://backend')
        
        while True:
            # First string recieved is socket ID of client
            client_id = self.socket.recv()
            request = self.socket.recv()
            #self.processMessage(client_id, request.decode('ascii'))
            self.processMessage(client_id, request)

    # this message is not thread-safe
    def sendMsg(self, client_id, msg):
        self.socket.send(client_id.encode('ascii'), zmq.SNDMORE)
        self.socket.send(msg)

    def processMessage(self, client_id, msg):
        self.parent.msg_recv_callback(client_id, msg)

def msg_recvd(client_id, msg):
    server.sendMsg(client_id, "ACK")

if __name__ == '__main__':
    global server
    server = Server(msg_recvd)
    server.start()

