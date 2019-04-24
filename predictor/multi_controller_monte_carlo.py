import sys
sys.path.insert(0, "/home/harshitg/Courses/CS6422/cs6422_project/")

from distributions.latency_dist import ControllerServerLatencyDist

import argparse
import yaml

import random
import numpy as np
import time
import threading

## Defining the constants
SAMPLE_SIZE=1000

####### Auxiliary variables for simulation ######
# Store all transactions with their time stamps on a dictionary, value = transaction_timestamp, key = transaction_id
TRANS_START_TS = {}
# Dictionary of key = txn_id and value = list of servers for that txn
SERVERS_PER_TRANSACTION = {}
# counter of transaction failures
transaction_failures = 0
# list of tuples: transactions that failed against other transaction in pairs (failed_txn, conflict_txn) 
failures_data = []

latency_dist = None

def generate_poisson_events(rate, N, W, sample_size):
    global TRANS_START_TS, SERVERS_PER_TRANSACTION, SAMPLE_SIZE
    SAMPLE_SIZE = sample_size
    # Use to create transaction_id identifiers
    transaction_number = 1
    transaction_timestamp = 0 # We maintain virtual time (in milliseconds)
    while(transaction_number < SAMPLE_SIZE):
        transaction_id = transaction_number
        transaction_number += 1
        beta = 1/rate
        txn_inter_time = np.random.poisson(beta)
        transaction_timestamp += txn_inter_time # Increment the time , no need to sleep
        TRANS_START_TS[transaction_id] = transaction_timestamp
        SERVERS_PER_TRANSACTION[transaction_id] = random.sample(range(N), W) # Populate which servers are updated by this transaction
     
def servers_intersect(txn1, txn2):
    global SERVERS_PER_TRANSACTION
    return bool(set(SERVERS_PER_TRANSACTION[txn1]) & set(SERVERS_PER_TRANSACTION[txn2]))

def check_conditions():
    global TRANS_START_TS
    # Store the result of validation for each transaction
    valid_result = {}

    # First sample the latency values for each transaction 
    latencies = {}
    for txn_id in TRANS_START_TS.keys():
        valid_result[txn_id] = None
        l0 = compute_latency()
        l1 = compute_latency()
        latencies[txn_id] = (l0, l1)

    # Now we need to sort the transactions based on when their validation request arrives at the validator
    valid_req_arrivals = []
    for txn_id in TRANS_START_TS.keys():
        valid_req_arrival_ts = TRANS_START_TS[txn_id] + latencies[txn_id][0]
        valid_req_arrivals.append((txn_id, valid_req_arrival_ts))

    valid_req_arrivals = sorted(valid_req_arrivals, key=lambda x: x[1])

    for valid_req_idx in range(len(valid_req_arrivals)):
        curr_txn_id = valid_req_arrivals[valid_req_idx][0]
        servers_updated = {}
        for server in SERVERS_PER_TRANSACTION[curr_txn_id]:
            servers_updated[server] = False
        # Find transaction that conflicts with this one

        # ONLY NEED TO LOOK IN PAST AS WE ARE ITERATING BY ARRIVAL TIME OF VALIDATION REQ
        conflicter = valid_req_idx-1
        while conflicter >= 0:
            conflicter_txn_id = valid_req_arrivals[conflicter][0]
            assert valid_result[conflicter_txn_id] != None
            if valid_result[conflicter_txn_id]: # we consider this potential conflicter only if it succeeded validation
                # calculate the time when conflicter's update reached controller generating the current transaction
                update_reach_ts = TRANS_START_TS[conflicter_txn_id] + latencies[conflicter_txn_id][0] + latencies[conflicter_txn_id][1]
                if servers_intersect(curr_txn_id, conflicter_txn_id):
                    if update_reach_ts > TRANS_START_TS[curr_txn_id]:
                        valid_result[curr_txn_id] = False
                        break

                    for server in SERVERS_PER_TRANSACTION[conflicter_txn_id]:
                        if server in SERVERS_PER_TRANSACTION[curr_txn_id]:
                            servers_updated[server] = True

                    all_done = True
                    for server in servers_updated.keys():
                        if not servers_updated[server]:
                            all_done = False

                    if all_done:
                        valid_result[curr_txn_id] = True
                        break

            conflicter -= 1

        if conflicter < 0:
            valid_result[curr_txn_id] = True
 
    return valid_result

def compute_latency():
    ################################# ENTER AVERAGE AND STANDARD DEVIATION OF LATENCY DISTRIBUTION #######################################
    # gets a random number of a uniform distribution with the same parameters: average and standar deviation = 0.5 and 2.5 respectively
    latency = latency_dist.sample()
    return latency
    
def start_servers(transaction_id, total_servers, number_of_tasks):

    # We will randomly select the servers that will be assigned to this transasction and store them in the hashMap SERVERS_PER_TRANSACTION
    list_of_servers = []
    for i in range(number_of_tasks):
        selected_server = np.random.randint(0, total_servers)
        print("Server %d was selected for transaction %s"%(selected_server, transaction_id))
        list_of_servers.append(selected_server)
    SERVERS_PER_TRANSACTION[transaction_id] = list_of_servers
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monte Carlo simulation for OCC conflict probability in multi-controller setting')
    parser.add_argument('--poisson-rate', dest='poisson_rate', type=float, help='Rate of Poisson process generating transactions. Note that time units are in milliseconds')
    parser.add_argument('-N', dest='N', type=int, help='Number of servers in total infrastructure', default=5)
    parser.add_argument('-W', dest='W', type=int, help='Number of servers updated by each transaction', default=3)
    parser.add_argument('-S', dest='sample_size', type=int, help='Sample size(number of transactions)', default=10000)
    parser.add_argument('-L', dest='latency', type=float, help='Average latency between controller and validator (in milliseconds)', default=10.0)
    args = parser.parse_args()

    latency_dist = ControllerServerLatencyDist(args.latency, 1)

    generate_poisson_events(args.poisson_rate, args.N, args.W, args.sample_size)
    
    # Once all transactions and tasks are 'executed' in servers, and therefore data structures are populated, 
    # we call method check_conditions, which will check for conflicts between transactions that could leed to txn failure
    valid_result = check_conditions()
    successes = 0
    for txn_id in valid_result.keys():
        if valid_result[txn_id]:
            successes += 1

    print ("Success probability = %f"%(successes*1.0/len(valid_result)))
    
    # print failure data
    #print("Total failures of 5 transactions - defined as sample size - are: %d"%transaction_failures)
    #print("Further info on failures is follows this structure (failed transaction, conflicting transaction).....")
    #print(failures_data)
