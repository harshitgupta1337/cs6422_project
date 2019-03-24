from predictor.single_controller import *
from distributions.latency_dist import ControllerServerLatencyDist
from statistics import mean
import matplotlib.pyplot as plt

def plot_data(x_data, y_data):
    plt.plot(x_data, y_data, color='g')
    plt.xlabel('values')
    plt.ylabel('probablity average ')
    plt.title('title goes here')
    plt.show()

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
     
    #number of features = 6
    #we change one feature per plot
    #for example change the value of W
    x_data = []
    y_data = []
    for i in range(0, 5):
        p = SingleControllerPredictor(N, i, itt, auto_rate, num_trials, lat_mean, lat_stddev)
        prob_list = p.generate_predictions()
        print mean(prob_list)
        y_data.append(mean(prob_list))
        x_data.append(i)

    plot_data(x_data, y_data)

if __name__ == "__main__":
    main()
