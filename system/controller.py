import threading
import queue
import time
import random

import argparse
import yaml

from state.server_state import *
#from two_phase_commit.proto.commit_protocol_pb2 import *
from two_phase_commit.twoPhaseCommit import *
from comm.server_instance import *
from proto.messages_pb2 import *

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
    def __init__(self, transaction_id, version_map, tasks):
        self.dependencies = set()
        self.version_map = version_map
        self.transaction_id = transaction_id
        self.tasks = tasks

class Controller:
    def __init__(self, N, w, url):

        self.url = url
        self.N = N
        self.w = w
        self.server_state = {}
        self.server_url_to_id = {}
        self.transaction_id_counter = 0
        #self.init_servers(server_data)
        self.executing_transactions = {}
        self.pending_transactions = {}
        self.pending_trans_condition = threading.Condition()

        self.commit_protocol = twoPhaseCommit("controller", self.send_cp_msg, self.on_transaction_complete, None)

        self.request_queue = queue.Queue()
        self.req_queue_condition = threading.Condition()
        self.request_handler = RequestHandler(self.request_queue, self.req_queue_condition, self.process_request)
        self.request_handler.start()

        self.trans_exec_thread = threading.Thread(target=self.transaction_executor)
        self.trans_exec_thread.start()

        self.server_socket = Server(self.url, self.on_recv_msg)
        self.server_socket.start()

    def __del__(self):
        self.request_handler.join()

    def on_init_server_msg(self, msg):
        init_server = msg.init_server
        server_url = init_server.server_url
        server_idx = len(self.server_state)
        # TODO need to add a lock here 
        self.server_state[server_idx] = ServerState(server_idx, init_server.cpu, init_server.memory, server_url)
        self.server_url_to_id[server_url] = server_idx
        print ("Registered server %s with CPU=%d memory=%d"%(server_url, init_server.cpu, init_server.memory))

    def on_recv_msg(self, src, data):
        msg = Message()
        msg.ParseFromString(data)
        #print ("Received msg of type %d"%(msg.type))
        if msg.type == Message.INIT_SERVER:
            self.on_init_server_msg(msg)
        if msg.type == Message.APP_REQ:
            self.on_app_req(msg)
        if msg.type == Message.COMMIT_PROTOCOL:
            cp_msg = msg.cp_msg
            self.commit_protocol.onRcvMsg(msg.src, cp_msg)

    def send_cp_msg(self, dst, cp_msg):
        msg = Message()
        msg.type = Message.COMMIT_PROTOCOL
        msg.cp_msg.CopyFrom(cp_msg)
        self.send_msg(dst, msg)
    
    def send_msg(self, dst, msg):
        self.server_socket.sendMsg(dst, msg.SerializeToString())

    def on_transaction_complete(self, trans_id, success, server_replies):
        print ("Transaction %d complete"%trans_id)
        self.executing_transactions.pop(trans_id, None)
        if not success:
            self.process_transaction_failure(trans_id, server_replies)
        else:
            self.process_transaction_success(trans_id, server_replies)

    def select_servers(self, request):
        server_idxs = random.sample(range(self.N), self.w)
        return server_idxs

    def increment_server_versions(self, server_idxs):
        for server_idx in server_idxs:
            self.server_state[server_idx].version.v1 += 1

    def process_request(self, request):
        servers = self.select_servers(request)
        self.update_servers(servers)

    def update_servers(self, server_idxs):
        version_map = {}
        for server_idx in server_idxs:
            self.server_state[server_idx].version.v1 += 1
            version_map[server_idx] = self.server_state[server_idx].version

        transaction_id = self.transaction_id_counter
        self.transaction_id_counter += 1
        
        # Create tasks for transaction
        
        tasks = []
        task_id = 0
        for server_idx in server_idxs:
            task = Task()
            task.task_id = task_id
            #TODO Assign the real server address here :)
            task.server = self.server_state[server_idx].server_url
            task.task_type = Task.CREATE_APP
            task.version.CopyFrom(self.server_state[server_idx].version)

            tasks.append(task)
            task_id+=1

        self.submit_transaction(transaction_id, version_map, tasks)

    def on_app_req(self, msg):
        
        if len(self.server_state) < self.N:
            print ("Unable to submit request")
            return
        self.request_queue.put(msg)

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
    def submit_transaction(self, transaction_id, version_map, tasks):
        t = TransactionStruct(transaction_id, version_map, tasks)
        map_t = version_map.keys()

        self.pending_trans_condition.acquire()
        for e in self.executing_transactions.keys():
            map_e = self.executing_transactions[e].version_map.keys()
            if bool(set(map_t) & set(map_e)):
                # there is an overlap
                t.dependencies.add(self.executing_transactions[e].transaction_id)

        for p in self.pending_transactions.keys():
            map_p = self.pending_transactions[p].version_map.keys()
            if bool(set(map_t) & set(map_p)):
                # there is an overlap
                t.dependencies.add(self.pending_transactions[p].transaction_id)

        self.pending_transactions[transaction_id] = t
        self.pending_trans_condition.notify()
        self.pending_trans_condition.release()

    def process_transaction_failure(self, transaction_id, server_replies):
        self.req_queue_condition.acquire()
        self.pending_trans_condition.acquire()
        print ("Transaction %d FAILED :("%transaction_id)
    
        dependents = []

        pending_ids = self.pending_transactions.keys()
        sorted_ids = sorted(pending_ids)

        for pend_trans_id in sorted_ids:
            if transaction_id in self.pending_transactions[pend_trans_id].dependencies:
                dependents.append(pend_trans_id)
            elif bool(set(dependents) & set(self.pending_transactions[pend_trans_id].dependencies)):
                dependents.append(pend_trans_id)

        for dependency in dependents:
            self.pending_transactions.pop(dependency, None)
            for pend_trans_id in self.pending_transactions.keys():
                if dependency in self.pending_transactions[pend_trans_id].dependencies:
                    self.pending_transactions[pend_trans_id].dependencies.remove(dependency)

        # 2. Resubmit their request
        for dependency in dependents:
            self.process_request(None)

        for server in server_replies:
            server_id = self.server_url_to_id[server]
            self.server_state[server_id].version.CopyFrom(server_replies[server].curr_version)

        self.pending_trans_condition.release()
        self.req_queue_condition.release()

    def process_transaction_success(self, transaction_id, server_replies):
        #  TODO update the version ???
        self.req_queue_condition.acquire()

        self.pending_trans_condition.acquire()
        for pend_trans_id in self.pending_transactions.keys():
            if transaction_id in self.pending_transactions[pend_trans_id].dependencies:
                self.pending_transactions[pend_trans_id].dependencies.remove(transaction_id)
        self.pending_trans_condition.notify()
        self.pending_trans_condition.release()
        self.req_queue_condition.release()

    def execute_transaction(self, trans_id, trans_struct):
        self.executing_transactions[trans_id] = trans_struct
        print ("Executing %s"%trans_id)
        self.commit_protocol.submitTransaction(trans_struct)

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
                for pend_trans_id in to_execute:
                    trans_struct = self.pending_transactions[pend_trans_id]
                    self.pending_transactions.pop(pend_trans_id, None)
                    self.execute_transaction(pend_trans_id, trans_struct)
            self.pending_trans_condition.release()        

def merge_args(yaml_conf, cmdline_args):
    if cmdline_args.w:
        yaml_conf['w'] = cmdline_args.w
    if cmdline_args.N:
        yaml_conf['N'] = cmdline_args.N
    #if cmdline_args.server_data:
    #    yaml_conf['server_data'] = cmdline_args.server_data
    return yaml_conf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Independent controller instance')
    parser.add_argument('-N', dest='N', type=int, help='Number of servers (overrides conf file)')
    parser.add_argument('-w', dest='w', type=int, help='Size of write set  (overrides conf file)')
    #parser.add_argument('--server-conf', dest='server_data', type=str, help='Path to server conf  (overrides conf file)')
    parser.add_argument('--conf', dest='conf', type=str, help='Path to config file')
    args = parser.parse_args()

    yaml_stream = None
    if args.conf:
        yaml_stream = open(args.conf, "r")
    yaml_conf = yaml.load(yaml_stream)

    args_dict = merge_args(yaml_conf, args)
    
    controller = Controller(args_dict['N'], args_dict['w'], args_dict['url'])
    #controller = Controller(args_dict['N'], args_dict['w'], args_dict['server_data'], args_dict['url'])

    while True:
        controller.submit_request(None)
        time.sleep (1)
