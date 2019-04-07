import threading
import queue
import time
import random

import argparse
import yaml

from proto.commit_protocol_pb2 import *

class RequestHandler(threading.Thread):
    def __init__(self, request_queue, req_queue_mutex, func, *args, **kwargs):
        self.request_queue = request_queue
        self.req_queue_mutex = req_queue_mutex
        self.callback = func
        super().__init__(*args, **kwargs)

    def run(self):
        while True:
            req = self.request_queue.get()
            print ("Was able to read an item")
            self.callback(req)



class Controller:
    def __init__(self, N, w, server_data):

        self.N = N
        self.w = w
        self.server_state = {}
        self.init_servers(server_data)

        self.request_queue = queue.Queue()
        self.req_queue_condition = threading.Condition()
        self.request_handler = RequestHandler(self.request_queue, self.req_queue_condition, self.process_request)
        self.request_handler.start()

    def __del__(self):
        self.request_handler.join()

    def select_servers(self, request):
        server_idxs = random.sample(range(self.N), self.w)
        return server_idxs

    def process_request(self, request):
        servers = self.select_servers(request)
        

    def submit_request(self, request):
        self.request_queue.put(request)

    def init_servers(self, server_data_file):
        yaml_stream = None
        yaml_stream = open(server_data_file, "r")
        server_conf = yaml.load(yaml_stream)
        idx = 0
        for server in server_conf:
            self.server_state[idx] = server
            idx += 1
        
def merge_args(yaml_conf, cmdline_args):
    if cmdline_args.w:
        yaml_conf['w'] = cmdline_args.w
    if cmdline_args.N:
        yaml_conf['N'] = cmdline_args.N
    if cmdline_args.server_data:
        yaml_conf['server_data'] = cmdline_args.server_data
    return yaml_conf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Independent controller instance')
    parser.add_argument('-N', dest='N', type=int, help='Number of servers (overrides conf file)')
    parser.add_argument('-w', dest='w', type=int, help='Size of write set  (overrides conf file)')
    parser.add_argument('--server-conf', dest='server_data', type=str, help='Path to server conf  (overrides conf file)')
    parser.add_argument('--conf', dest='conf', type=str, help='Path to config file')
    args = parser.parse_args()

    yaml_stream = None
    if args.conf:
        yaml_stream = open(args.conf, "r")
    yaml_conf = yaml.load(yaml_stream)

    args_dict = merge_args(yaml_conf, args)
    
    controller = Controller(args_dict['N'], args_dict['w'], args_dict['server_data'])
    while True:
        controller.submit_request(None)
        time.sleep (1)
        print ("Iteration of main thread")
