import numpy as np
import time
import threading
####### Auxiliary variables for simulation ######
# Store all transactions with their time stamps on a dictionary, value = transaction_timestamp, key = transaction_id
transaction_and_timestamps = {}
# Dictionary of key = txn_id and value = list of servers for that txn
servers_per_transaction = {}
# counter of transaction failures
transaction_failures = 0
# list of tuples: transactions that failed against other transaction in pairs (failed_txn, conflict_txn) 
failures_data = []

def poisson_process(application_id, auto_rate, start):

	#Each application is running a unique thread with application_id 
	print("Application with id: %s started. Auto rate = %f" %(application_id,auto_rate))
	
	# Use to create transaction_id identifiers
	transaction_number = 1
	################################################# ENTER SIZE OF SAMPLE ################################################
	sample_size = 5
	while(transaction_number < sample_size):
		transaction_id = application_id + (".%s"%transaction_number)
		transaction_number += 1
		beta = 1/auto_rate
		txn_inter_time = np.random.poisson(beta)
		print("Waiting for next transaction in application %s to arrive... Arrival in %f" %(application_id, txn_inter_time))
		time.sleep(txn_inter_time)
		transaction_timestamp = time.time()
		transaction_and_timestamps[transaction_id] = transaction_timestamp
		start(transaction_id, transaction_timestamp)
		
	# Once all transactions and tasks are assigned and 'executed' in servers, and therefore data structures are populated, 
	# we are done with this method
	
def start(transaction_id, transaction_timestamp):

	# ¿How many servers are there for use?
	total_servers = 5
	# ¿How  many tasks does a transaction have? -> Constant for now, future approach: give it as an input when txn thread is created. 
	# Assumption: Each task is executed entirelt on a single server
	number_of_tasks = 3
	
	# Each transaction will execute start_servers algorithm to select randomly the set of servers that will be executing the transaction's tasks
	print("Starting set of %d servers for transaction %s "%(number_of_tasks, transaction_id))
	start_servers(transaction_id, total_servers, number_of_tasks)
	
	# Execute txn's tasks in servers
	for server in servers_per_transaction[transaction_id]: 
		hello_world(transaction_id, server)
	
	# once all tasks are 'executed' in each designated server, we are done with this method

def check_conditions():
		
	# Calculate the maximum latency at the moment to check for conflicts that could led the txn to fail, given the average and the SD
	max_latency = compute_max_latency(0.5, 2.5)
	
	# Check first condition: t2_startime + LC2[0] < t1_startime + LC1[0] meaning that t2 arrives first to validator
	for t1 in transaction_and_timestamps.keys():
		# 1. Calculate latencies LC1 and LC2
		latency_t1_0 = compute_latency()
		latency_t1_1 = compute_latency()
		latency_t2_0 = compute_latency()
		latency_t2_1 = compute_latency()
		# 2. Get timestamps of t_current (t1) and define window of vulnerability
		t1_timestamp = transaction_and_timestamps[t1]
		inferior_limit = t1_timestamp - (2 * max_latency) # two times because it has to get to the validator first and then to the other controller
		superior_limit = t1_timestamp + (2 * max_latency)
		# 3. Check condition on range (inferior_limit, superior_limit)
		for t2 in transaction_and_timestamps.keys():
			# if t2 is within range and is not t1 then check if meets condition 1
			if(transaction_and_timestamps[t2] >= inferior_limit and transaction_and_timestamps[t2] <= superior_limit and t2 != t1):
				# check server conflict for potential transaction conflict 
				if(check_condition_1(t1, t2) == True):
					check_condition_2(t1, t2, latency_t1_0, latency_t1_1, latency_t2_0, latency_t2_1)
				else: 
					print("No conflict between transaction %s and transaction %s"%(t1, t2))

def check_condition_1(t1, t2):
	for server in servers_per_transaction[t1]:
		for conflict_server in servers_per_transaction[t2]:
			if(server == conflict_server):
				return True
	return False
		
def check_condition_2(t1, t2, latency_t1_0, latency_t1_1, latency_t2_0, latency_t2_1):
	if((transaction_and_timestamps[t2] + latency_t2_0) < (transaction_and_timestamps[t1] + latency_t1_0)):
		check_condition_3(t1, t2, latency_t1_0, latency_t1_1, latency_t2_0, latency_t2_1)
	else: 
		print("No conflict between transaction %s and transaction %s"%(t1, t2))

def check_condition_3(t1, t2, latency_t1_0, latency_t1_1, latency_t2_0, latency_t2_1):
	# Check third condition: t2_startime + LC2[0] + lC2[1] > t1_startime meaning that t1 got validated and was sent to other controller after it sent t1 to validator
	if((transaction_and_timestamps[t2] + latency_t2_0 + latency_t2_1) > transaction_and_timestamps[t1]):
		# t1 would fail because of t2
		print("Transaction %s would fail because of conflict with transaction %s"%(t1, t2))
		transaction_failures += 1
		pair = (t1, t2)
		failures_data.append(pair)
	else: 
		print("No conflict between transaction %s and transaction %s"%(t1, t2))
		

def hello_world(transaction_id, server): 
	# This function simulates that the txn was sent to the server in order to execute, in this case print 'hello world'
	print("Hello world from transaction %s executing a task in server %d"%(transaction_id, server))
	
######### CHANGE: No need to recompute the average -> gaussian distribution: calculate the max directly
def compute_max_latency(avg, sd):
	# the average and standard deviation are fixed
	max_latency = avg + 2.5 * sd
	return max_latency

def compute_latency():
	################################# ENTER AVERAGE AND STANDARD DEVIATION OF LATENCY DISTRIBUTION #######################################
	# gets a random number of a uniform distribution with the same parameters: average and standar deviation = 0.5 and 2.5 respectively
	latency = np.random.uniform(0.5, 2.5)
	return latency
	
def start_servers(transaction_id, total_servers, number_of_tasks):

	# We will randomly select the servers that will be assigned to this transasction and store them in the hashMap servers_per_transaction
	list_of_servers = []
	for i in range(number_of_tasks):
		selected_server = np.random.randint(0, total_servers)
		print("Server %d was selected for transaction %s"%(selected_server, transaction_id))
		list_of_servers.append(selected_server)
	servers_per_transaction[transaction_id] = list_of_servers
	
if __name__ == "__main__":

	###### CHANGE: Add a variable per TASK that is a timestamp to check for conflicts between tasks
	###### Then report conflicts 


	print("Testing monte_carlo simulation with multiple threads")
	# Simulate the entry of applications, each with subsequent transactions 
	t1 = threading.Thread(target = poisson_process, args = ("001", 0.1, start,))
	t1.start()
	t2 = threading.Thread(target = poisson_process, args = ("002", 0.5, start,))
	t2.start()
	t3 = threading.Thread(target = poisson_process, args = ("003", 0.9, start,))
	time.sleep(10)
	t3.start()
	
	# Once all transactions and tasks are 'executed' in servers, and therefore data structures are populated, 
	# we call method check_conditions, which will check for conflicts between transactions that could leed to txn failure
	check_conditions()
	
	# print failure data
	print("Total failures of 5 transactions - defined as sample size - are: %d"%transaction_failures)
	print("Further info on failures is follows this structure (failed transaction, conflicting transaction).....")
	print(failures_data)

	
	
