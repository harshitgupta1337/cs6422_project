from predictor.single_controller import *
from distributions.latency_dist import ControllerServerLatencyDist
import numpy

N = None
W = None
auto_rate = None

server_latency_dists = []
server_last_update_ts = {}
server_last_latency_sample = {}

trans_attempts = {}

def generate_transaction_arrivals(num_transactions):
    arrivals = []
    '''
    t = 10
    for i in range(num_transactions):
        arrivals.append(t)
        t += 40
    '''
    intensity = 45
    curr_ts = 0.0
    for ts in numpy.random.poisson(intensity, num_transactions):
        curr_ts += ts
        arrivals.append(curr_ts)
    return arrivals

def run_system():
    current_time = 0
    current_trans = 0

def update_server_staleness(server_idx, second_phase_start_ts, latencies):
    global server_last_update_ts, server_last_latency_sample
    server_last_update_ts[server_idx] = second_phase_start_ts + latencies[2]
    server_last_latency_sample[server_idx] = latencies[3]

def get_prob_changed(server_idx, trans_start_ts, trans_idx, latencies, auto_rate):
    if server_idx not in server_last_update_ts.keys():
        return 0.0
    else:
        window = trans_start_ts + latencies[0] - server_last_update_ts[server_idx]
        exponent = -1 * auto_rate * window
        return (1 - math.exp(exponent))

# This function should return the transaction completion time
def process_transaction(trans_idx, trans_start_ts):
    global trans_attempts
    trans_finish_time = trans_start_ts
    while (True):
        if trans_idx not in trans_attempts.keys():
            trans_attempts[trans_idx] = 0
        trans_attempts[trans_idx] += 1

        server_idxs = random.sample(range(N), W)
        
        prob_success = 1
       
        latency_samples = {}
 
        phase_2_start_time = trans_start_ts

        for server_idx in server_idxs:
            latencies = server_latency_dists[server_idx].sample(4)
            latency_samples[server_idx] = latencies
            phase_1_reply_recv_ts = latencies[0]+latencies[1]+trans_start_ts 
            if phase_1_reply_recv_ts >= phase_2_start_time:
                phase_2_start_time = phase_1_reply_recv_ts

            prob_changed = get_prob_changed(server_idx, trans_start_ts, trans_idx, latencies, auto_rate)
            prob_success *= (1 - prob_changed)
   
        for server_idx in latency_samples.keys(): 
            update_server_staleness(server_idx, phase_2_start_time, latency_samples[server_idx])
       
        trans_finish_time = phase_2_start_time
        for server_idx in latency_samples.keys():
            ack_recv_time = phase_2_start_time + latency_samples[server_idx][2] + latency_samples[server_idx][3]
            if ack_recv_time >= trans_finish_time:
                trans_finish_time = ack_recv_time
 
        r = random.uniform(0,1)
  
        if r >= prob_success:
            #  transaction has failed
            trans_start_ts = trans_finish_time
        else:
            break

    # Transaction trans_idx is finished
    return trans_finish_time

def main():
    global N, W, auto_rate, lat_mean, lat_stddev
    N = 500
    W = 1
    auto_rate = 0.00001 # this is per millisecond
    lat_mean = 10
    lat_stddev = 0.0001

    num_transactions = 10000
 
    for i in range(N):
        server_latency_dists.append(ControllerServerLatencyDist(lat_mean, lat_stddev))

    transaction_arrivals = generate_transaction_arrivals(num_transactions)

    curr_time = 0.0
    last_finished_trans_idx = -1

    total_latency = 0.0
    trans_idx = 0
    while trans_idx < num_transactions:
        if last_finished_trans_idx < 0:
            curr_time = transaction_arrivals[0]
        else:
            next_trans_idx = last_finished_trans_idx+1
            if transaction_arrivals[next_trans_idx] > curr_time:
                curr_time = transaction_arrivals[next_trans_idx]

        finish_time = process_transaction(trans_idx, curr_time)
        trans_execn_latency = finish_time - transaction_arrivals[trans_idx]
        #print ("TransID\t", trans_idx, "\tstart_delay\t", "%.2f"%(curr_time-transaction_arrivals[trans_idx]), "\tlatency\t", "%.2f"%trans_execn_latency, "\tnum_trials\t", trans_attempts[trans_idx])
        curr_time = finish_time
        last_finished_trans_idx = trans_idx
        trans_idx += 1
        total_latency += trans_execn_latency

    total = 0.0
    for trans_idx in range(1, num_transactions):
        total += transaction_arrivals[trans_idx] - transaction_arrivals[trans_idx-1]
    mean_inter_arrival = total/num_transactions
    print (mean_inter_arrival)
    print (total_latency/num_transactions)

if __name__ == "__main__":
    main()
