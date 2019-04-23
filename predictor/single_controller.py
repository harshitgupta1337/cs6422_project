from distributions.latency_dist import *
import operator as op
from functools import reduce
import random, math

ncr_cache = {}

def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    result = numer/denom
    return result

'''
    Model for single-controller scenario
'''
class SingleControllerPredictor:
    '''
        Initialize latency distributions for controller-server pairs
    '''
    def initialize_server_latency_dists(self, ctrl_server_lat_mean, ctrl_server_lat_stddev):
        for server_idx in range(self.N):
            self.server_latency_dists.append(ControllerServerLatencyDist(ctrl_server_lat_mean, ctrl_server_lat_stddev))

    def __init__ (self, N, W, inter_trans_time, auto_rate, 
                    num_trials, ctrl_server_lat_mean, ctrl_server_lat_stddev):
        self.N = N
        self.W = W
        self.inter_trans_time = inter_trans_time
        self.auto_rate = auto_rate
        self.num_trials = num_trials
        self.inf = 1000
        
        self.server_latency_dists = []
        self.initialize_server_latency_dists(ctrl_server_lat_mean, ctrl_server_lat_stddev)
   
    '''
        The probability of a server being last chosen by k-th previous transaction
        k has to be >= 1 
    '''
    def get_prob_last_change_k(self, k):
        prob = 1
        #not_chosen = float(ncr(self.N-1, self.W))/float(ncr(self.N, self.W))
        not_chosen = 1 - float(self.W)/float(self.N)
        for i in range(k-1):
            prob *= not_chosen
        prob *= (1 - not_chosen)
        return prob

    '''
        The probability of autonomous change on server 
    '''
    def get_prob_auto_change(self, k, server_idx):
        latency_dist = self.server_latency_dists[server_idx]

        exponent = -1 * self.auto_rate * (k*self.inter_trans_time + latency_dist.sample() - latency_dist.sample() - latency_dist.sample() - latency_dist.sample())
        return (1 - math.exp(exponent))

    '''
        Calculate probability of transaction success
    '''
    def generate_single_prediction(self):
        prob_not_changed = 1

        server_idxs = random.sample(range(self.N), self.W)

        for server_idx in server_idxs:
            total_change_prob = 0.0
            for k in range(1, self.inf):
                prob_s_changed = self.get_prob_last_change_k(k)
                prob_auto_change = self.get_prob_auto_change(k, server_idx)
                total_change_prob += prob_s_changed * prob_auto_change

            prob_not_changed *= (1-total_change_prob)

        return prob_not_changed
        #return (1 - prob_not_changed)

    '''
        Generate predictions of transaction success probabilities
    '''
    def generate_predictions(self):
        probs = []
        for trial in range(self.num_trials):
            prob = self.generate_single_prediction()
            probs.append(prob)
        return probs
