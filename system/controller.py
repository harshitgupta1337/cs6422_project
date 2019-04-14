import threading
import queue
import time
import random

import argparse
import yaml

from state.server_state import *
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
            self.callback(req)

class TransactionStruct:
    def __init__(self, transaction_id, version_map):
        self.dependencies = set()
        self.version_map = version_map
        self.id = transaction_id

class Controller:
    def __init__(self, N, w, server_data):

        self.N = N
        self.w = w
        self.server_state = {}
        self.transaction_id_counter = 0
        self.init_servers(server_data)
        self.executing_transactions = {}
        self.pending_transactions = {}
        self.pending_trans_condition = threading.Condition()

        self.request_queue = queue.Queue()
        self.req_queue_condition = threading.Condition()
        self.request_handler = RequestHandler(self.request_queue, self.req_queue_condition, self.process_request)
        self.request_handler.start()
        

        self.trans_exec_thread = threading.Thread(target=self.transaction_executor)
        self.trans_exec_thread.start()

    def __del__(self):
        self.request_handler.join()

    def select_servers(self, request):
        server_idxs = random.sample(range(self.N), self.w)
        return server_idxs

    def increment_server_versions(self, server_idxs):
        for server_idx in server_idxs:
            self.server_state[server_idx].version.v1 += 1
        print (self.server_state[server_idx].version.v1)

    def process_request(self, request):
        servers = self.select_servers(request)
        self.update_servers(servers)

    def update_servers(self, server_idxs):
        version_map = {}
        for server_idx in server_idxs:
            version = self.server_state[server_idx].version
            version_map[server_idx] = version

        transaction_id = self.transaction_id_counter
        self.transaction_id_counter += 1
        self.submit_transaction(transaction_id, version_map)

    def submit_request(self, request):
        self.request_queue.put(request)

    def init_servers(self, server_data_file):
        yaml_stream = None
        yaml_stream = open(server_data_file, "r")
        server_conf = yaml.load(yaml_stream)
        idx = 0
        for server in server_conf:
            cpu = server["cpu"]
            memory = server["memory"]
            self.server_state[idx] = ServerState(idx, cpu, memory)
            idx += 1

    # Transaction code
    def submit_transaction(self, transaction_id, version_map):
        t = TransactionStruct(transaction_id, version_map)
        map_t = version_map.keys()

        for e in self.executing_transactions.keys():
            map_e = self.executing_transactions[e].version_map.keys()
            if bool(set(map_t) & set(map_e)):
                # there is an overlap
                t.dependencies.add(self.executing_transactions[e].id)

        for p in self.pending_transactions.keys():
            map_p = self.pending_transactions[p].version_map.keys()
            if bool(set(map_t) & set(map_p)):
                # there is an overlap
                t.dependencies.add(self.pending_transactions[p].id)

        print ("Adding transaction id %d to pending transactions"%transaction_id)
        self.pending_trans_condition.acquire()
        self.pending_transactions[transaction_id] = t
        self.pending_trans_condition.notify()
        self.pending_trans_condition.release()

    def process_transaction_failure(self, transaction_id, server_replies):
        pass

    def process_transaction_success(self, transaction_id, server_replies):
        pass

    def transaction_executor(self):
        while True:
            self.pending_trans_condition.acquire()
            to_execute = []
            for pend_trans_id in self.pending_transactions.keys():
                if len(self.pending_transactions[pend_trans_id].dependencies) == 0:
                    to_execute.append(pend_trans_id)
            
            if len(to_execute) == 0:
                self.pending_trans_condition.wait()
            else:
                # process the transactions in to_execute
                self.executing_transactions[pend_trans_id] = self.pending_transactions[pend_trans_id]
                self.pending_transactions.pop(pend_trans_id, None)
                print ("Executing %s"%pend_trans_id)
            self.pending_trans_condition.release()        

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
