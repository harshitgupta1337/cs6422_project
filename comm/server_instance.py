#!/usr/bin/env python

import threading

import zmq

class Server(object):
    def __init__(self):
        self.zmq_context = zmq.Context()
    
    def start(self):
        
        #Instantiate workers, Accept client connections, distribute computation requests among workers, route computed results back to clients.
        
        # Front facing socket to accept client connections.
        socket_front = self.zmq_context.socket(zmq.ROUTER)
        socket_front.bind('tcp://127.0.0.1:5001')
        
        # Backend socket to distribute work.
        socket_back = self.zmq_context.socket(zmq.DEALER)
        socket_back.bind('inproc://backend')
        
        # Start three workers.
        for i in range(1,4):
            worker = Worker(self.zmq_context, i)
            worker.start()
        
        # Read a client's socket ID and request. => Send socket ID and request to a worker. => Read a client's socket ID and result from a worker. => Route result back to the client using socket ID.
        zmq.device(zmq.QUEUE, socket_front, socket_back)

class Worker(threading.Thread):
    
    def __init__(self, zmq_context, _id):
        threading.Thread.__init__(self)
        self.zmq_context = zmq_context
        self.worker_id = _id
    
    def run(self):
        #Socket to communicate with front facing server.
        socket = self.zmq_context.socket(zmq.DEALER)
        socket.connect('inproc://backend')
        
        while True:
            # First string recieved is socket ID of client
            client_id = socket.recv()
            request = socket.recv()
            print('Worker ID - %s. Recieved computation request.' % (self.worker_id))
            result = self.SendMsg(request)
            print('Worker ID - %s. Sending computed result back.' % (self.worker_id))
            
            #For successful routing of result to correct client, the socket ID of client should be sent first.
            
            socket.send(client_id, zmq.SNDMORE)
            socket.send(result)

    def SendMsg(self, request):
        #SendMsg (dest, message)
        #used by the controller/server to send message to some other entity "dest"
        #replace request with  (dest, message)
        #socket.send(dest, zmq.SNDMORE)
        #socket.send(result)
        #request-->message
        numbers = request.split(':')
        return str(int(numbers[0]) + int(numbers[1]))

if __name__ == '__main__':
    server = Server().start()
