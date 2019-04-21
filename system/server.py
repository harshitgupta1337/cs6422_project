import threading
import queue
import time
import random

import argparse
import yaml

from state.server_state import *
from two_phase_commit.proto.commit_protocol_pb2 import *
from two_phase_commit.twoPhaseCommit import *
from comm.client_instance import *

class Server:
    def __init__(self, url, controller_url):
        self.url = url
        self.controller_url = controller_url
        self.client_socket = Client(url, self.on_msg_recv, self.controller_url)

        self.init_connection()

    def on_msg_recv(self, src, msg):
        print ("received msg from %s" % src)

    def init_connection(self) :
        #Prepare init message
        init_msg = "INIT"
        self.client_socket.sendMsg(init_msg)
        

def merge_args(yaml_conf, cmdline_args):
    #if cmdline_args.url:
    #    yaml_conf['url'] = cmdline_args.url
    #if cmdline_args.controller_url:
    #    yaml_conf['controller_url'] = cmdline_args.controller_url
    return yaml_conf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('--conf', dest='conf', type=str, help='Path to config file')
    args = parser.parse_args()

    yaml_stream = None
    if args.conf:
        yaml_stream = open(args.conf, "r")
    yaml_conf = yaml.load(yaml_stream)

    args_dict = merge_args(yaml_conf, args)
   
    controller_url = args_dict["controller_url"]
    url = args_dict["url"]

    server = Server(url, controller_url)
