from predictor.single_controller import *
from distributions.latency_dist import ControllerServerLatencyDist
from statistics import mean
import matplotlib.pyplot as plt

def plot_data(x_data, y_data):
    plt.plot(x_data, y_data, color='g', label = 'W')
    plt.legend(loc='upper right')
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

    #for example change the value of lat_stddev
    x_data = []
    y_data = []
    prob_list = []
    for i in range(0, 5):
        p = SingleControllerPredictor(N, W, itt, auto_rate, num_trials, lat_mean, i)
        prob_list = p.generate_predictions()
        print mean(prob_list)
        y_data.append(mean(prob_list))
        x_data.append(i)
    plt.plot(x_data, y_data, color='k', label = 'lat_stddev')

    plt.legend(loc='upper right')
    plt.xlabel('values')
    plt.ylabel('probablity average ')
    plt.title('title goes here')
    plt.show()
    
if __name__ == "__main__":
    main()
