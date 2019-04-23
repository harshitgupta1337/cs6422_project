import sys
sys.path.insert(0, "/home/harshitg/Courses/CS6422/cs6422_project/system")

from proto.commit_protocol_pb2 import *

from twoPhaseCommit import *

def commHandler(server, msg):
    print ("Now I will send a message to server %s"%server)

def trans_complete(trans_id):
    print ("Transaction %d was complete"%trans_id)

if __name__ == "__main__":

	num_tasks = 3
	cp_2pc = twoPhaseCommit("2pc", commHandler, trans_complete)
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
	cp_2pc = twoPhaseCommit("2pc", commHandler, trans_complete)
    
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
