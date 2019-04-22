#!/usr/bin/env python

import threading
import time
from random import choice

import zmq

class Client(object):
    def __init__(self, identity, msg_recv_callback, server_socket_url):
        self.msg_recv_callback = msg_recv_callback
        self.identity = identity.encode('ascii')
        self.zmq_context = zmq.Context()
        self.server_socket_url = server_socket_url

        self.worker = ClientWorker(self.zmq_context, self.identity, self, self.server_socket_url)
        self.worker.start()

    def sendMsg(self, data):
        self.worker.send(data)
 
class ClientWorker(threading.Thread):
    def __init__(self, zmq_context, identity, parent, server_socket_url):
        threading.Thread.__init__(self)
        self.identity = identity
        self.zmq_context = zmq_context
        self.parent = parent
        self.server_socket_url = server_socket_url
   
    def run(self):
        #Connects to server.
        self.socket = self.get_connection()
       
        #self.send('%s:%s' % (num1, num2))
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
       
        # Polling is used to check for sockets with data before reading because socket.recv() is blocking.
        while True:
            # Poll for 5 seconds. Return any sockets with data to be read.
            sockets = dict(poller.poll(5000))
            
            # If socket has data to be read.
            if self.socket in sockets and sockets[self.socket] == zmq.POLLIN:
                result = self.receive(self.socket)

                self.parent.msg_recv_callback(result)
        
        self.socket.close()
        self.zmq_context.term()

    def send(self, data):
        #Send data through provided socket.
        self.socket.send(data)

    def receive(self, socket):
        #Recieve and return data through provided socket.
        return socket.recv()

    def get_connection(self):
        #Create a zeromq socket of type DEALER; set it's identity, connect to server and return socket.
        socket = self.zmq_context.socket(zmq.DEALER)
        socket.setsockopt(zmq.IDENTITY, self.identity)
        socket.connect(self.server_socket_url)
        return socket
    
    def callback(self):
        # code to call when it receives a message.
        number_list = range(0,10)
        num1 = choice(number_list)
        num2 = choice(number_list)
        return num1, num2

def foo(msg):
    print ("Message received at time = %s"%time.time())

if __name__ == '__main__':
    # Instantiate three clients with different ID's.
    i = 1
    client = Client(str("tcp://127.0.0.1:600%d"%i), foo)
    time.sleep(1)

    for i in range(0,100):
        print ("sending msg at time %s"%time.time())
        client.sendMsg("%d:%d"%(i,i))
        time.sleep(1)

