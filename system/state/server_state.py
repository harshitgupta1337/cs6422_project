import sys
sys.path.insert(0, "/home/harshitg/Courses/CS6422/cs6422_project/system")

from proto.commit_protocol_pb2 import *

'''
    This class stores the state of a server
'''
class ServerState:
    
    def __init__(self, server_id, max_cpu, max_memory, url):
        self.server_id = server_id
        self.server_url = url
        self.allocations = {}
        self.max_cpu = max_cpu
        self.max_memory = max_memory
        self.version = Version()
        self.version.v1 = 0
        self.version.v2 = 0

    def update_allocation(self, task_id, cpu, memory):
        if cpu > max_cpu or memory > max_mamory:
            return False

        self.allocations[task_id] = (cpu, memory)
        return True

    def get_allocation(self, task_id):
        return self.allocations[task_id]

    def is_allocated(self, task_id):
        return self.allocations.has_key(task_id)
