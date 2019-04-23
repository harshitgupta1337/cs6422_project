from predictor.single_controller import *
from distributions.latency_dist import ControllerServerLatencyDist
import numpy

'''
    This class simulates an end-to-end single-controller scenario.
    Communication with servers is emulated as an activity that takes up logical time. 
    Failure probability of each transaction is calculated assuming Possion arrival of autonomous updates and by using window of inconsistency. 
'''
class SystemSimulator:
    def __init__(self, N, W, num_trans, mean_itt, auto_rate, latency_mean, latency_stddev, always_success=False):
        self.mean_itt = mean_itt
        self.num_transactions = num_trans
        self.W = W
        self.N = N
        self.auto_rate = auto_rate
        self.latency_mean = latency_mean
        self.latency_stddev = latency_stddev
        self.server_latency_dists = []
        self.trans_attempts = {}
        for i in range(N):
            self.server_latency_dists.append(ControllerServerLatencyDist(latency_mean, latency_stddev))
        self.server_last_update_ts = {}
        self.server_last_latency_sample = {}
        self.always_success = always_success
        self.prob_success_arr = []

    '''
        Generates the time instants when a transaction arrives at the controller instance
    '''
    def generate_transaction_arrivals(self, num_transactions):
        arrivals = []
        intensity = self.mean_itt
        curr_ts = 0.0
        # Assumes a Poisson arrival process
        for ts in numpy.random.poisson(intensity, num_transactions):
            curr_ts += ts
            arrivals.append(curr_ts)
        return arrivals
    
    '''
        Updates the staleness values for a server given when the 2nd phase of transaction starts
    '''
    def update_server_staleness(self, server_idx, second_phase_start_ts, latencies):
        self.server_last_update_ts[server_idx] = second_phase_start_ts + latencies[2]
        self.server_last_latency_sample[server_idx] = latencies[3]
    
    '''
        Gets probability that an autonomous change occurred on a server before the phase 1 msg for transaction reaches the server
    '''
    def get_prob_changed(self, server_idx, trans_start_ts, trans_idx, latencies):
        if server_idx not in self.server_last_update_ts.keys():
            return 0.0
        else:
            # Calculating the window of vulnerability
            window = trans_start_ts + latencies[0] - self.server_last_update_ts[server_idx]
            exponent = -1 * self.auto_rate * window
            return (1 - math.exp(exponent))
    
    '''
        Process an incoming transaction. Performs multiple trials of execution on servers until success.
        This function should return the transaction completion time
    '''
    def process_transaction(self, trans_idx, trans_start_ts):
        global trans_attempts
        trans_finish_time = trans_start_ts
        while (True):    # iterate until transaction succeeds
            if trans_idx not in self.trans_attempts.keys():
                self.trans_attempts[trans_idx] = 0
            self.trans_attempts[trans_idx] += 1
   
            # Select the servers that this transaction would affect 
            server_idxs = random.sample(range(self.N), self.W)
            
            prob_success = 1
           
            latency_samples = {}
     
            phase_2_start_time = trans_start_ts
    
            for server_idx in server_idxs:
                latencies = self.server_latency_dists[server_idx].sample(4)
                latency_samples[server_idx] = latencies
                phase_1_reply_recv_ts = latencies[0]+latencies[1]+trans_start_ts 
                # Calculating the time when Phase 2 starts
                if phase_1_reply_recv_ts >= phase_2_start_time:
                    phase_2_start_time = phase_1_reply_recv_ts
    
                # Calculating probability of autonomous updates on this server
                prob_changed = self.get_prob_changed(server_idx, trans_start_ts, trans_idx, latencies)
                prob_success *= (1 - prob_changed)
       
            for server_idx in latency_samples.keys(): 
                self.update_server_staleness(server_idx, phase_2_start_time, latency_samples[server_idx])
           
            trans_finish_time = phase_2_start_time
            for server_idx in latency_samples.keys():
                ack_recv_time = phase_2_start_time + latency_samples[server_idx][2] + latency_samples[server_idx][3]
                # Calculating the time when transaction processing would end, i.e. end of Phase 2
                if ack_recv_time >= trans_finish_time:
                    trans_finish_time = ack_recv_time
     
            r = random.uniform(0,1)
            
            #print ("Prob of success of transId ", trans_idx, " = ", prob_success)
            self.prob_success_arr.append(prob_success)
            if r >= prob_success and (not self.always_success):
                #  transaction has failed
                trans_start_ts = trans_finish_time
            else:
                break
    
        # Transaction trans_idx is finished
        return trans_finish_time
    
    def run(self):
        transaction_arrivals = self.generate_transaction_arrivals(self.num_transactions)
    
        curr_time = 0.0
        last_finished_trans_idx = -1
    
        total_latency = 0.0
        trans_idx = 0
        while trans_idx < self.num_transactions:
            if last_finished_trans_idx < 0:
                curr_time = transaction_arrivals[0]
            else:
                next_trans_idx = last_finished_trans_idx+1
                if transaction_arrivals[next_trans_idx] > curr_time:
                    curr_time = transaction_arrivals[next_trans_idx]
    
            finish_time = self.process_transaction(trans_idx, curr_time)
            trans_execn_latency = finish_time - transaction_arrivals[trans_idx]
            #print ("TransID\t", trans_idx, "\tstart_delay\t", "%.2f"%(curr_time-transaction_arrivals[trans_idx]), "\tlatency\t", "%.2f"%trans_execn_latency, "\tnum_trials\t", self.trans_attempts[trans_idx])
            curr_time = finish_time
            last_finished_trans_idx = trans_idx
            trans_idx += 1
            total_latency += trans_execn_latency
    
        total = 0.0
        for trans_idx in range(1, self.num_transactions):
            total += transaction_arrivals[trans_idx] - transaction_arrivals[trans_idx-1]
        mean_inter_arrival = total/self.num_transactions
        #print (mean_inter_arrival)
        #print (total_latency/self.num_transactions)
        return (self.prob_success_arr, mean_inter_arrival, total_latency/self.num_transactions)
