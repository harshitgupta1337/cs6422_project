from proto.commit_protocol_pb2 import *

class twoPhaseCommit:

    def __init__(self, name, messageSendCallback, transactionCompleteCallback, function):
        self.name = name
        self.messageSendCallback = messageSendCallback
        self.transactionCompleteCallback = transactionCompleteCallback
        self.transaction_data = {}
        self.phase1_replies = {}
        self.phase2_replies = {}
        self.function = function
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


    #CONTROLLER SIDE functionS
    def handle_ack(self, trans_id, server, cp_msg):
        print ("Received Ack for trans Id %d from server %s" %(trans_id, server))
        if trans_id not in self.phase2_replies:
            self.phase2_replies[trans_id] = {}
        self.phase2_replies[trans_id][server] = cp_msg

        if self.phase2_complete(trans_id):
            self.transactionCompleteCallback(trans_id, self.transaction_success)
			
    def phase1_complete(self, trans_id):
        if(len(self.phase1_replies[trans_id].keys()) == len(self.transaction_data[trans_id].tasks)):
            print("Phase 1 complete")
            return True
        else:
            print("Phase 1 incomplete")
            return False
				
    def handle_agreement(self, trans_id, server, cp_msg):
        print ("Received Agreement for trans Id %d from server %s" %(trans_id, server))
        if trans_id not in self.phase1_replies: self.phase1_replies[trans_id] = {}
        self.phase1_replies[trans_id][server] = CommitProtocolMessage.AGREEMENT
		
        if(self.phase1_complete(trans_id)): self.start_phase2(trans_id)
   
    def handle_disagreement(self, trans_id, server, cp_msg):
        print ("Received disagreement for trans Id %d from server %s" %(trans_id, server))
        if(trans_id not in self.phase1_replies): self.phase1_replies[trans_id] = {}
        self.phase1_replies[trans_id][server] = CommitProtocolMessage.DISAGREEMENT

        if(self.phase1_complete(trans_id)): self.start_phase2(trans_id)

    
    def start_phase2(self, trans_id):
		# Need to check whether all servers replied with agreement or not
	    for server in self.phase1_replies[trans_id].keys():
	        if(self.phase1_replies[trans_id][server] == CommitProtocolMessage.DISAGREEMENT):
	            self.transaction_success = False
	            print("CONTROLLER: Server %s disagreed to commit. Sending abort order to all servers..."%server)
	        if(self.phase1_replies[trans_id][server] == CommitProtocolMessage.AGREEMENT):
	            print("CONTROLLER: Server %s agreed to commit. Waiting for other servers to respond..."%server)
				
	    if(self.transaction_success): 
		######################################################################new#########################################################################
		##################### construct msg and sendMsg to server (abort or commit) - txn id and task id (one msg per task id)
	        print("CONTROLLER: All servers agreed. Ready to start phase 2. Preparing commit messages for all servers...")
	        for task in self.transaction_data[trans_id].tasks:
	            cp_msg = CommitProtocolMessage ()
	            cp_msg.type = CommitProtocolMessage.COMMIT
	            cp_msg.transaction_id = trans_id
	            cp_msg.commit.task_id = task.task_id
	            #cp_msg.success = True
	            self.sendMsg("controller", task.server, cp_msg)
	    else: 
		######################################################################new#########################################################################
	        print("CONTROLLER: Not all servers agreed. Preparing abort messages for all servers...")
	        for task in self.transaction_data[trans_id].tasks:
		        cp_msg = CommitProtocolMessage()
		        cp_msg.type = CommitProtocolMessage.ABORT
		        cp_msg.transaction_id = trans_id
		        cp_msg.abort.task_id = task.task_id
		        #cp_msg.success = False
		        self.sendMsg("controller", task.server, cp_msg)

    def phase2_complete(self, trans_id):
        if len(self.phase2_replies[trans_id].keys()) == len(self.transaction_data[trans_id].tasks):
            return True
        else:
            return False	
			
    #SERVER SIDE functionS
    def handle_commit(self, trans_id, server, cp_msg):
        print("SERVER %s: Received commit order from controller. Commit transaction with id %d" %(server, trans_id))
		#next step is to send an abort from server to controller
    def handle_abort(self, trans_id, server, cp_msg): 
        print ("SERVER %s: Received abort order from controller. Abort transaction with id %d" %(server, trans_id))   
		#next step is to send an ACK from server to controller

    # For now we just flip a coin to determine if a txn is completed or not, by the time the server gets the commit request from the controller,
    # as that is out of the scope for our project. Being realistic, 
    # success/failure of a transaction would depend on application. Lets assume all transactions are completed successfully in this case	
    def handle_commit_req(self, trans_id, server, cp_msg): 
        print ("SERVER %s: Commit request has been received"%server)
		#Execute the task in server, OBS: delete field success in cp_msg message in proto file
        self.process(cp_msg, function, server)
		
    def process(self, cp_msg, function, server):
	######################################################NEW#########################################################################################
		# We can't assume that this function will return a value, nor that it will return eventually - don't want to stall
        self.function(cp_msg.commit_req)

    # Txn wasn't completed by server, next step is to disagree to commit request
    def taskFailCallback(self, task_id, trans_id, server, server_reply):
        print("Transaction %d was NOT completed by the server %s"%(trans_id, server))
	######################################################NEW#########################################################################################
        cp_msg = CommitProtocolMessage()
        cp_msg.type = CommitProtocolMessage.DISAGREEMENT
        cp_msg.transaction_id = trans_id
        cp_msg.disagreement.task_id = task_id
        cp_msg.disagreement.server_reply.CopyFrom(server_reply)
        self.sendMsg("controller", server, cp_msg)   
		
    # Txn was completed by server, next step is to agree to commit request
    def taskSuccessCallback(self, task_id, trans_id, server, server_reply):
        print("Transaction %d was successfully completed by the server %s"%(trans_id, server))
	######################################################NEW#########################################################################################
        cp_msg = CommitProtocolMessage()
        cp_msg.type = CommitProtocolMessage.AGREEMENT
        cp_msg.transaction_id = trans_id
        cp_msg.agreement.task_id = task_id
        cp_msg.agreement.server_reply.CopyFrom(server_reply)
        self.sendMsg("controller", server, cp_msg)
		
    def sendMsg(self, destination, src, cp_msg):
        print("Sending message of type %s to %s from %s"%(cp_msg.type, destination, src))
			
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

def commHandler(server, msg):
    print ("Now I will send a message to server %s"%server)

def trans_complete(trans_id, state):
    print ("Transaction %d was complete with state %s"%(trans_id, state))

def function(commit_req): 
    print("function on task %d called"%commit_req.task.task_id)

if __name__ == "__main__":

	num_tasks = 3
	cp_2pc = twoPhaseCommit("2pc", commHandler, trans_complete, function)
	# TEST CASE 1: Transasction is successful
	print("############################### TEST CASE 1: TRANSACTION IS SUCCESSFUL #################################################")
    
    # Step 1 : controller submits a transaction
	print("######## Testing controller submitting transaction ########")
	trans_id = 1
	trans = Transaction()
	trans.transaction_id = trans_id

	
	for i in range(num_tasks):
		task = trans.tasks.add()
		task.task_id = i
		task.server = "10.100.1.20%d"%i
		task.task_type = Task.CREATE_APP

	cp_2pc.submitTransaction(trans)
	
	# step 1.5 : server executes transaction
	
	# step 1.75 : controller sends commit request 
	print("######## Testing controller sending commit requests ########")

	for i in range(num_tasks):
		server =  "10.100.1.20%d"%i
		cp_msg = CommitProtocolMessage()
		cp_msg.transaction_id = trans_id
		cp_msg.type = CommitProtocolMessage.COMMIT_REQ
		
		req = CommitReq()
		req.task_id = i
		#Added a new attribute for testing purposes (user will decide whether the txn fails or succeeds for now)
		#req.success = True
		cp_msg.commit_req.CopyFrom(req)
		cp_msg.success = True
		cp_2pc.onRcvMsg(server, cp_msg)
		
    # step 2 : server submits an agreement
	print("######## Testing server submitting agreement ########")

	for i in range(num_tasks):
		server =  "10.100.1.20%d"%i
		cp_msg = CommitProtocolMessage()
		cp_msg.transaction_id = trans_id
		cp_msg.type = CommitProtocolMessage.AGREEMENT
		
		agr = Agreement()
		agr.task_id = i
		cp_msg.agreement.CopyFrom(agr)
		cp_2pc.onRcvMsg(server, cp_msg)
	
	# step 2.5 : controller checks agreements and commits transaction
	print("####### Testing controller sending commit order to all servers #######")
	
	for i in range(num_tasks):
		server =  "10.100.1.20%d"%i
		cp_msg = CommitProtocolMessage()
		cp_msg.transaction_id = trans_id
		cp_msg.type = CommitProtocolMessage.COMMIT

		com = Commit()
		com.task_id = i
		cp_msg.commit.CopyFrom(com)
		cp_2pc.onRcvMsg(server, cp_msg)
	
    # step 3 : submitting an ack
	for i in range(num_tasks):
		server =  "10.100.1.20%d"%i
		cp_msg = CommitProtocolMessage()
		cp_msg.transaction_id = trans_id
		cp_msg.type = CommitProtocolMessage.ACK

		ack = Ack()
		ack.task_id = i
		cp_msg.ack.CopyFrom(ack)

		cp_2pc.onRcvMsg(server, cp_msg)
		
		
		
			
	# TEST CASE 2: Transasction is not successful
	print("############################### TEST CASE 2: TRANSACTION IS UNSUCCESSFUL #################################################")
	cp_2pc = twoPhaseCommit("2pc", commHandler, trans_complete, function)
    
    # Step 1 : controller submits a transaction
	print("######## Testing controller submitting transaction ########")
	trans_id = 1
	trans = Transaction()
	trans.transaction_id = trans_id

	num_tasks = 3
	for i in range(num_tasks):
		task = trans.tasks.add()
		task.task_id = i
		task.server = "10.100.1.20%d"%i
		task.task_type = Task.CREATE_APP

	cp_2pc.submitTransaction(trans)
	
	# step 1.5 : server executes transaction
	
	# step 1.75 : controller sends commit request 
	print("######## Testing controller sending commit requests ########")

	for i in range(num_tasks):
		server =  "10.100.1.20%d"%i
		cp_msg = CommitProtocolMessage()
		cp_msg.transaction_id = trans_id
		cp_msg.type = CommitProtocolMessage.COMMIT_REQ
		
		req = CommitReq()
		req.task_id = i
		# Only server 10.100.1.202 will not complete the txn and therefore fail
		cp_msg.commit_req.CopyFrom(req)
		if(i == 2): cp_msg.success = False
		else: cp_msg.success = True
		cp_2pc.onRcvMsg(server, cp_msg)
		
    # step 2 : one server submits a disagreement
	print("######## Testing servers submitting two agreements and a disagreement ########")

	# two agreements
	for i in range(num_tasks - 1):
		server =  "10.100.1.20%d"%i
		cp_msg = CommitProtocolMessage()
		cp_msg.transaction_id = trans_id

		cp_msg.type = CommitProtocolMessage.AGREEMENT
		agr = Agreement()
		agr.task_id = i
		cp_msg.agreement.CopyFrom(agr)
		cp_2pc.onRcvMsg(server, cp_msg)
		
	# one disagreement
	server =  "10.100.1.202"
	cp_msg = CommitProtocolMessage()
	cp_msg.transaction_id = trans_id

	cp_msg.type = CommitProtocolMessage.DISAGREEMENT
	dis = Disagreement()
	dis.task_id = i
	cp_msg.disagreement.CopyFrom(dis)
	cp_2pc.onRcvMsg(server, cp_msg)
	
	# step 2.5 : controller checks agreements and aborts transaction
	print("####### Testing controller sending abort order to all servers #######")
	
	for i in range(num_tasks):
		server =  "10.100.1.20%d"%i
		cp_msg = CommitProtocolMessage()
		cp_msg.transaction_id = trans_id
		cp_msg.type = CommitProtocolMessage.ABORT

		ab = Abort()
		com.task_id = i
		cp_msg.abort.CopyFrom(ab)
		cp_2pc.onRcvMsg(server, cp_msg)
	
    # step 3 : submitting an ack
	for i in range(num_tasks):
		server =  "10.100.1.20%d"%i
		cp_msg = CommitProtocolMessage()
		cp_msg.transaction_id = trans_id
		cp_msg.type = CommitProtocolMessage.ACK

		ack = Ack()
		ack.task_id = i
		cp_msg.ack.CopyFrom(ack)

		cp_2pc.onRcvMsg(server, cp_msg)