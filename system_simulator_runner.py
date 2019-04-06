from predictor.system_simulator import *
from read_args import *
from distributions.latency_dist import ControllerServerLatencyDist
import numpy
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        (N, W, mean_itt, auto_rate, num_transactions, lat_mean, lat_stddev) = read_args(sys.argv)
    else:
        N = 10
        W = 2
        auto_rate = 0.0001 # this is per millisecond
        lat_mean = 10
        lat_stddev = 0.0001
        mean_itt = 1000
        num_transactions = 10000
    sim = SystemSimulator(N, W, num_transactions, mean_itt, auto_rate, lat_mean, lat_stddev, True)
    (prob_success_arr, mean_itt, avg_latency) = sim.run()
    print ("Median prob_success = %.3f"%numpy.median(prob_success_arr))
