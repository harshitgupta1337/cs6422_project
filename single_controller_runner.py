from predictor.single_controller import *
from distributions.latency_dist import ControllerServerLatencyDist

def main():

    N = 100
    W = 4
    itt = 100
    auto_rate = 0.00001 # this is per millisecond
    num_trials = 10
    lat_mean = 10
    lat_stddev = 4

    p = SingleControllerPredictor(N, W, itt, auto_rate, num_trials, lat_mean, lat_stddev)
    print (p.generate_predictions())

if __name__ == "__main__":
    main()
