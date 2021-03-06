import sys
from predictor.single_controller import *
from distributions.latency_dist import ControllerServerLatencyDist
from read_args import *
import numpy
from statistics import mean

def plot_data(x_data, y_data):
    plt.plot(x_data, y_data, color='g', label = 'W')
    plt.legend(loc='upper right')
    plt.xlabel('values')
    plt.ylabel('probablity average ')
    plt.title('title goes here')
    plt.show()


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
    print ("Median prob_success = %.3f"%numpy.median(prob_success_arr))

    ''' 
    #number of features = 6
    #we change one feature per plot
    
    #for example change the value of W
    x_data = []
    y_data = []
    prob_list = []
    for i in range(0, 5):
        p = SingleControllerPredictor(N, i, itt, auto_rate, num_trials, lat_mean, lat_stddev)
        prob_list = p.generate_predictions()
        #print mean(prob_list)
        y_data.append(mean(prob_list))
        x_data.append(i)
    plt.plot(x_data, y_data, color='g', label = 'W')

    #for example change the value of itt
    x_data = []
    y_data = []
    prob_list = []
    for i in range(0, 5):
        p = SingleControllerPredictor(N, W, i, auto_rate, num_trials, lat_mean, lat_stddev)
        prob_list = p.generate_predictions()
        #print mean(prob_list)
        y_data.append(mean(prob_list))
        x_data.append(i)
    plt.plot(x_data, y_data, color='c', label = 'itt')

    #for example change the value of auto_rate
    x_data = []
    y_data = []
    prob_list = []
    for i in range(0, 5):
        p = SingleControllerPredictor(N, W, itt, i, num_trials, lat_mean, lat_stddev)
        prob_list = p.generate_predictions()
        #print mean(prob_list)
        y_data.append(mean(prob_list))
        x_data.append(i)
    plt.plot(x_data, y_data, color='y', label = 'auto_rate')

    #change the value of num_trials


    #for example change the value of lat_mean
    x_data = []
    y_data = []
    prob_list = []
    for i in range(0, 5):
        p = SingleControllerPredictor(N, W, itt, auto_rate, num_trials, i, lat_stddev)
        prob_list = p.generate_predictions()
        print mean(prob_list)
        y_data.append(mean(prob_list))
        x_data.append(i)
    plt.plot(x_data, y_data, color='m', label = 'lat_mean')

    plot_data(x_data, y_data)
    ''' 
    plt.legend(loc='upper right')
    plt.xlabel('values')
    plt.ylabel('probablity average ')
    plt.title('title goes here')
    plt.show()
    
if __name__ == "__main__":
    main()
