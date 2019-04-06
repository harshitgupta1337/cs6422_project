from proto.commit_protocol_pb2 import *

def handle_agreement(trans_id, agreement):
    print ("received agremeent message for transaction id %d; cmd_id = %d"%(trans_id, agreement.command_id))
    print ("Agreement contains server reply with some_field = %d "%(agreement.server_reply.some_field))

# Function called when the controller recvs  a msg
# and then passes it to the 2PC commit protocol
def on_recv_msg(cp_msg):
    msg_type = cp_msg.type
    trans_id = cp_msg.transaction_id
    if msg_type == CommitProtocolMessage.AGREEMENT:
        assert cp_msg.HasField("agreement")
        handle_agreement(trans_id, cp_msg.agreement)

if __name__ == "__main__":

    # In this snippet, we'll be constructing an agreement
    # supposed to be sent from server to controller
    cp_msg = CommitProtocolMessage()
    cp_msg.type = CommitProtocolMessage.AGREEMENT
    cp_msg.transaction_id = 2

    #Now building the actual Agreement message
    agr = Agreement()
    agr.command_id = 0
    
    agr.server_reply.some_field = 12 # directly creating ServerReply inside the Agreement by initializing agreement's field

    cp_msg.agreement.CopyFrom(agr)

    # Now submitting the msg to 2PC 
    on_recv_msg(cp_msg)
