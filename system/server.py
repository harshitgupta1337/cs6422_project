import threading
import queue
import time
import random

import argparse
import yaml

from state.server_state import *
from proto.commit_protocol_pb2 import *
from two_phase_commit.twoPhaseCommit import *
from comm.client_instance import *
from proto.messages_pb2 import *

class Server:
    def __init__(self, url, controller_url, cpu, memory):
        self.url = url
        self.cpu = cpu
        self.memory = memory
        self.controller_url = controller_url
        self.client_socket = Client(url, self.on_msg_recv, self.controller_url)

        self.commit_protocol = twoPhaseCommit(self.url, self.send_cp_msg, None, self.command_arrival)
        self.init_connection()

    def command_arrival(self, cp_msg):
        print ("Command arrived on server ", self.url)
        trans_id = cp_msg.transaction_id
        cmd_id = cp_msg.commit_req.task_id
        server_reply = ServerReply()
        server_reply.some_field = 0
        self.commit_protocol.commandComplete(trans_id, cmd_id, True, server_reply)

    def send_cp_msg(self, dst, cp_msg):
        msg = Message()
        msg.type = Message.COMMIT_PROTOCOL
        msg.cp_msg.CopyFrom(cp_msg)
        self.client_socket.sendMsg(msg.SerializeToString())

    def on_msg_recv(self, msg_str):
        msg = Message()
        msg.ParseFromString(msg_str)
        if msg.type == Message.COMMIT_PROTOCOL:
            cp_msg = msg.cp_msg
            self.commit_protocol.onRcvMsg(msg.src, cp_msg)

    def init_connection(self) :
        #Prepare init message
        init_msg = Message()
        init_msg.type = Message.INIT_SERVER
        init_msg.init_server.server_url = self.url
        init_msg.init_server.cpu = self.cpu
        init_msg.init_server.memory = self.memory
        self.client_socket.sendMsg(init_msg.SerializeToString())

def merge_args(yaml_conf, cmdline_args):
    if cmdline_args.cpu:
        yaml_conf['cpu'] = cmdline_args.cpu
    if cmdline_args.memory:
        yaml_conf['memory'] = cmdline_args.memory
    return yaml_conf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('--conf', dest='conf', type=str, help='Path to config file')
    parser.add_argument('--cpu', dest='cpu', type=int, help='Max cores')
    parser.add_argument('--memory', dest='memory', type=int, help='Max memory (KB)')
    args = parser.parse_args()

    yaml_stream = None
    if args.conf:
        yaml_stream = open(args.conf, "r")
    yaml_conf = yaml.load(yaml_stream)

    args_dict = merge_args(yaml_conf, args)
   
    controller_url = args_dict["controller_url"]
    url = args_dict["url"]
    cpu = args_dict["cpu"]
    memory = args_dict["memory"]

    server = Server(url, controller_url, cpu, memory)
    print ("Done with main")
