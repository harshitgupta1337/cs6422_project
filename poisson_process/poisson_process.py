import numpy as np
import time
import threading
def poisson_process(application_id, auto_rate, method_to_run):
	#Each application is running a unique thread with application_id 
	print("Application with id: %s started. Auto rate = %f" %(application_id,auto_rate))
	transaction_number = 1
	while(True):
		transaction_id = application_id + (".%s"%transaction_number)
		transaction_number += 1
		beta = 1/auto_rate
		txn_inter_time = np.random.poisson(beta)
		print("Waiting for next txn in application %s to arrive... Arrival in %f" %(application_id, txn_inter_time))
		time.sleep(txn_inter_time)
		method_to_run(transaction_id)
	
def hello_world(transaction_id):
	print("Hello world from transaction %s "%transaction_id)
	
if __name__ == "__main__":
	print("Testing poisson_process with multiple threaeds")
	t1 = threading.Thread(target = poisson_process, args = ("001", 0.1, hello_world,))
	t1.start()
	t2 = threading.Thread(target = poisson_process, args = ("002", 0.5, hello_world,))
	t2.start()
	t3 = threading.Thread(target = poisson_process, args = ("003", 0.9, hello_world,))
	time.sleep(10)
	t3.start()

	
	
