import sys
sys.path.insert(0, "/home/harshitg/Courses/CS6422/cs6422_project/system")

from proto.commit_protocol_pb2 import *

class twoPhaseCommit:

    def __init__(self, name, messageSendCallback, transactionCompleteCallback, commandArrival):
        self.name = name
        self.messageSendCallback = messageSendCallback
        self.transactionCompleteCallback = transactionCompleteCallback
        self.commandArrival = commandArrival
        self.transaction_data = {}
        self.phase1_replies = {}
        self.phase2_replies = {}
        self.transaction_success = True

    def prepareCommitReq(self, task, transaction_id, task_id):
        cp_msg = CommitProtocolMessage()
        cp_msg.type = CommitProtocolMessage.COMMIT_REQ
        cp_msg.transaction_id = transaction_id

        creq = CommitReq()
        creq.task.CopyFrom(task)
        creq.task_id = task_id
        cp_msg.commit_req.CopyFrom(creq)
    
        return cp_msg

    def submitTransaction (self, t):
        # Save the transaction
        self.transaction_data[t.transaction_id] = t
        'Step 1: Submit txn - The transaction is a set of tasks. Each task has a server assigned for execution'
        for task in t.tasks:
            commit_req_cp_msg = self.prepareCommitReq(task, t.transaction_id, task.task_id)
            # Update data strctures saying that phase 1 msg was sent to that server
            self.messageSendCallback(task.server, commit_req_cp_msg)

    #CONTROLLER SIDE FUNCTIONS
    def handle_ack(self, trans_id, server, cp_msg):
        #print ("Received Ack for trans Id %d from server %s" %(trans_id, server))
        if trans_id not in self.phase2_replies:
            self.phase2_replies[trans_id] = {}
        self.phase2_replies[trans_id][server] = cp_msg

        if self.phase2_complete(trans_id):
            success = True
            server_replies = {}
            for server in self.phase1_replies[trans_id].keys():
                if self.phase1_replies[trans_id][server].type == CommitProtocolMessage.DISAGREEMENT:
                    success = False
                    server_replies[server] = self.phase1_replies[trans_id][server].disagreement.server_reply
                if self.phase1_replies[trans_id][server].type == CommitProtocolMessage.AGREEMENT:
                    server_replies[server] = self.phase1_replies[trans_id][server].agreement.server_reply

            self.transactionCompleteCallback(trans_id, success, server_replies)
			
    def phase1_complete(self, trans_id):
        if(len(self.phase1_replies[trans_id].keys()) == len(self.transaction_data[trans_id].tasks)):
            #print("Phase 1 complete")
            return True
        else:
            #print("Phase 1 incomplete")
            return False
				
    def handle_agreement(self, trans_id, server, cp_msg):
        #print ("Received Agreement for trans Id %d from server %s" %(trans_id, server))
        if trans_id not in self.phase1_replies: self.phase1_replies[trans_id] = {}
        self.phase1_replies[trans_id][server] = cp_msg
		
        if(self.phase1_complete(trans_id)): self.start_phase2(trans_id)
   
    def handle_disagreement(self, trans_id, server, cp_msg):
        #print ("Received disagreement for trans Id %d from server %s" %(trans_id, server))
        if(trans_id not in self.phase1_replies): self.phase1_replies[trans_id] = {}
        self.phase1_replies[trans_id][server] = cp_msg

        if(self.phase1_complete(trans_id)): self.start_phase2(trans_id)

    
    def start_phase2(self, trans_id):
		# Need to check whether all servers replied with agreement or not
        transactionSuccess = True
        server_to_cmd_id = {}
        for server in self.phase1_replies[trans_id].keys():
            if(self.phase1_replies[trans_id][server].type == CommitProtocolMessage.DISAGREEMENT):
                server_to_cmd_id[server] = self.phase1_replies[trans_id][server].disagreement.task_id
                transactionSuccess = False
                #print("CONTROLLER: Server %s disagreed to commit. Sending abort order to all servers..."%server)
            if(self.phase1_replies[trans_id][server].type == CommitProtocolMessage.AGREEMENT):
                server_to_cmd_id[server] = self.phase1_replies[trans_id][server].agreement.task_id
                #print("CONTROLLER: Server %s agreed to commit. Waiting for other servers to respond..."%server)
				
        for server in self.phase1_replies[trans_id].keys():
            cpMsg = CommitProtocolMessage()
            cpMsg.transaction_id = trans_id
            if transactionSuccess:
                cpMsg.type = CommitProtocolMessage.COMMIT
                cpMsg.commit.task_id = server_to_cmd_id[server]
            else:
                cpMsg.type = CommitProtocolMessage.ABORT
                cpMsg.abort.task_id = server_to_cmd_id[server]
                
            self.messageSendCallback(server, cpMsg)

    def phase2_complete(self, trans_id) :
        if len(self.phase2_replies[trans_id].keys()) == len(self.transaction_data[trans_id].tasks):
            return True
        else:
            return False	
			
    #SERVER SIDE functionS
    def handle_commit(self, trans_id, server, cp_msg):
        #print("SERVER %s: Received commit order from controller. Commit transaction with id %d" %(server, trans_id))
        cp_msg = CommitProtocolMessage()
        cp_msg.type = CommitProtocolMessage.ACK
        cp_msg.ack.task_id = cp_msg.commit.task_id
        cp_msg.transaction_id = trans_id
        self.messageSendCallback(server, cp_msg)

    def handle_abort(self, trans_id, server, cp_msg): 
        #print ("SERVER %s: Received abort order from controller. Abort transaction with id %d" %(server, trans_id)) 
        cp_msg = CommitProtocolMessage()
        cp_msg.type = CommitProtocolMessage.ACK
        cp_msg.ack.task_id = cp_msg.commit.task_id
        cp_msg.transaction_id = trans_id
        self.messageSendCallback(server, cp_msg)

    def handle_commit_req(self, trans_id, server, cp_msg): 
        #print ("SERVER %s: Commit request has been received"%server)
		#Assuming that transaction has always completed successfully by the time the commit request arrives
        self.commandArrival(cp_msg)

    def commandComplete(self, trans_id, cmd_id, success, server_reply):
        cp_msg = CommitProtocolMessage()
        cp_msg.transaction_id = trans_id
        if success:
            cp_msg.type = CommitProtocolMessage.AGREEMENT
            cp_msg.agreement.task_id = cmd_id
            cp_msg.agreement.server_reply.CopyFrom(server_reply)
        else:
            cp_msg.type = CommitProtocolMessage.DISAGREEMENT
            cp_msg.disagreement.task_id = cmd_id
            cp_msg.disagreement.server_reply.CopyFrom(server_reply)

        self.messageSendCallback("controller", cp_msg)
			
    #GENERAL functionS
    def onRcvMsg(self, msg_src, cp_msg):
        msg_type = cp_msg.type
        trans_id = cp_msg.transaction_id
        if msg_type == CommitProtocolMessage.AGREEMENT:
            assert cp_msg.HasField("agreement")
            self.handle_agreement(trans_id, msg_src, cp_msg)
        if msg_type == CommitProtocolMessage.ACK:
            assert cp_msg.HasField("ack")
            self.handle_ack(trans_id, msg_src, cp_msg)
        if msg_type == CommitProtocolMessage.COMMIT_REQ:
            assert cp_msg.HasField("commit_req")
            self.handle_commit_req(trans_id, msg_src, cp_msg)
        if msg_type == CommitProtocolMessage.COMMIT:
            assert cp_msg.HasField("commit")
            self.handle_commit(trans_id, msg_src, cp_msg)
        if msg_type == CommitProtocolMessage.ABORT:
            assert cp_msg.HasField("abort")
            self.handle_abort(trans_id, msg_src, cp_msg)
        if msg_type == CommitProtocolMessage.DISAGREEMENT:
            assert cp_msg.HasField("disagreement")
            self.handle_disagreement(trans_id, msg_src, cp_msg)

