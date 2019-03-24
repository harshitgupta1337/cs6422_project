import sys
from predictor.single_controller import *
from distributions.latency_dist import ControllerServerLatencyDist
from read_args import *
import numpy

def main():

    if len(sys.argv) > 1:
        (N, W, itt, auto_rate, num_trials, lat_mean, lat_stddev) = read_args(sys.argv)
    else:
        N = 10
        W = 2
        itt = 1000
        auto_rate = 0.0001 # this is per millisecond
        num_trials = 10
        lat_mean = 10
        lat_stddev = 0.0001
    
    p = SingleControllerPredictor(N, W, itt, auto_rate, num_trials, lat_mean, lat_stddev)
    prob_success_arr = p.generate_predictions()
    print ("Median prob_success = ", numpy.median(prob_success_arr))

if __name__ == "__main__":
    main()
