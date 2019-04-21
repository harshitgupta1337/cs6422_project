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

class ReqGen:
    def __init__(self, url, controller_url):
        self.url = url
        self.controller_url = controller_url
        self.client_socket = Client(url, self.on_msg_recv, self.controller_url)

    def send_req(self):
        msg = Message()
        msg.type = Message.APP_REQ
        msg.app_request.app_id = "app"
        self.client_socket.sendMsg(msg.SerializeToString())
        print ("Sent request to controller")

    def on_msg_recv(self, src, msg):
        print ("received msg from %s" % src)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('--url', dest='url', type=str, help='')
    parser.add_argument('--controller-url', dest='controller_url', type=str, help='')
    args = parser.parse_args()

    reqgen = ReqGen(args.url, args.controller_url)

    while True:
        reqgen.send_req()
        time.sleep(1)
