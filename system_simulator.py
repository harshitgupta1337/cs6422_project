from predictor.single_controller import *
from distributions.latency_dist import ControllerServerLatencyDist

server_latency_dists = []
server_last_update_ts = {}
server_last_latency_sample = {}

def generate_transaction_arrivals(num_transactions):
    arrivals = []
    t = 10
    for i in range(num_transactions):
        arrivals.append(t)
        t += 100
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
        window = server_last_update_ts[server_idx] 
                + server_last_latency_sample[server_idx]  
                + latencies[0]

        exponent = -1 * auto_rate * window
        return (1 - math.exp(exponent))

# This function should return the transaction completion time
def process_transaction(trans_idx, trans_start_ts):
    trans_finish_time = trans_start_ts
    while (True):
        server_idxs = random.sample(range(self.N), self.W)
        
        prob_success = 1
       
        latency_samples = {}
 
        phase_2_start_time = trans_start_ts

        for server_idx in server_idxs:
            latencies = server_latency_dists[server_idx].sample(4)
            latency_samples[server_idx] = latencies
            phase_1_reply_recv_ts = latencies[0]+latencies[1]+trans_start_time 
            if phase_1_reply_recv_ts >= phase_2_start_time:
                phase_2_start_time = phase_1_reply_recv_ts

            prob_changed = get_prob_changed(server_idx, trans_start_ts, trans_idx, latencies)
            prob_success *= (1 - prob_changed)
   
        for server_idx in latency_samples.keys(): 
            update_server_staleness(server_idx, phase_2_start_time, latency_samples[server_idx])
       
        trans_finish_time = phase_2_start_time
        for server_idx in latency_samples.keys():
            ack_recv_time = phase_2_start_time + latency_samples[2] + latency_samples[3]
            if ack_recv_time >= trans_finish_time:
                trans_finish_time = ack_recv_time
 
        r = random.uniform(0,1)
    
        if r >= prob_success:
            #  transaction has failed
        else:
            break

    # Transaction trans_idx is finished
    rreturn trans_finish_time
    

def main():

    N = 100
    W = 4
    auto_rate = 0.00001 # this is per millisecond
    lat_mean = 10
    lat_stddev = 4

    transaction_arrivals = generate_transaction_arrivals(num_transactions)

    

    p = SingleControllerPredictor(N, W, itt, auto_rate, num_trials, lat_mean, lat_stddev)
    print (p.generate_predictions())

if __name__ == "__main__":
    main()
