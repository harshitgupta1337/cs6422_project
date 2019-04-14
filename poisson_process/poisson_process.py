import numpy as np
import time
	
def poisson_process(auto_rate, method_to_run):
	print("Auto rate = %f" %auto_rate)
	beta = 1/auto_rate
	print("Therefore beta = %f"%beta)
	txn_inter_time = np.random.poisson(beta)
	print("Going to sleep for %f seconds" %txn_inter_time)
	time.sleep(txn_inter_time)
	method_to_run()
	
def hello_world():
	print("Hello world")
	
if __name__ == "__main__":
	print("Testing np.random.poisson")
	auto_rate = 0.1
	while(auto_rate <= 1):
		poisson_process(auto_rate, hello_world)
		auto_rate += 0.1
	
	
