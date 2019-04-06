import sys, yaml
from os import mkdir
from os.path import join
from predictor.single_controller import *
from distributions.latency_dist import ControllerServerLatencyDist
from read_args import *
import numpy
from statistics import mean
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.font_manager import FontProperties

linestyles = ['-', '--', ':']
dot_linestyles = ['.']
markers = []
for m in Line2D.markers:
    try:
        if len(m) == 1 and m != ' ':
            markers.append(m)
    except TypeError:
        pass

styles = markers + [
    r'$\lambda$',
    r'$\bowtie$',
    r'$\circlearrowleft$',
    r'$\clubsuit$',
    r'$\checkmark$']

colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')

def plot_data(x_data, y_data):
    plt.plot(x_data, y_data, color='g')
    plt.xlabel('values')
    plt.ylabel('probablity average ')
    plt.title('title goes here')
    plt.show()

def plot_wrt_itt(data, labels, outfile_name):
    print ("Trying to plot")
    fig, ax = plt.subplots()
    ax.grid('on')
    ax.grid('on', which='minor')
    ax.grid('on', which='major')
    plt.minorticks_on()
    index=0
    for series in data:
        color = colors[index % len(colors)]
        linestyle = linestyles[index%len(linestyles)]
        ax.plot(series[0], series[1], linestyle, color=color, label=labels[index])
        index+=1

    handles, labels = ax.get_legend_handles_labels()
    lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5,-0.15) )
    xtitle = "Inter transaction time"
    plt.xlabel(xtitle, fontsize=14)
    ytitle = "Probability of siccess"
    plt.ylabel(ytitle, fontsize=14)
    plt.savefig(outfile_name, bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close(fig)

def save_datapoint(values, N, W, lat_mean, lat_stddev, itt, auto_rate, idx):
    foldername = join("dump", "datapoint_%d"%idx)
    mkdir (foldername)
    f = open(join(foldername, "conf.yaml"), 'w')
    conf = {}
    conf["N"] = N
    conf["W"] = W
    conf["lat_mean"] = lat_mean
    conf["auto_rate"] = auto_rate
    conf["itt"] = itt
    yaml.dump(conf,  f)
    '''
    f.write("N : %d\n"%N)
    f.write("W : %d\n"%W)
    f.write("lat_mean : %f\n"%lat_mean)
    f.write("lat_stddev : %f\n"%lat_stddev)
    f.write("itt : %f\n"%itt)
    f.write("auto_rate: %f\n"%auto_rate)
    '''
    f.close()

    f = open(join(foldername, "data.txt"), "w")
    for v in values:
        f.write("%s\n"%str(v))
    f.close()

def save_var_values(vals):
    with open(join("dump", "vals.yaml"), "w") as f:
        yaml.dump(vals, f)

def main():
    num_trials = 100
    lat_stddev = 0.1

    vals = {}
    vals["N"] = [100]
    vals["W"] = [2,4]
    vals["lat_mean"] = [10, 20]
    vals["auto_rate"] = [0.00001, 0.000001]
    vals["itt"] = [200, 400, 800]

    save_var_values(vals)

    idx = 0
    for N in vals["N"]:
        for W in vals["W"]:
            for lat_mean in vals["lat_mean"]:
                X = []
                Y = []
                labels = []
                for auto_rate in vals["auto_rate"]:
                    X.append([])
                    Y.append([])
                    labels.append("AutoRate = %f"%auto_rate)
                    for itt in vals["itt"]:
                        p = SingleControllerPredictor(N, W, itt, auto_rate, num_trials, lat_mean, lat_stddev)
                        prob_success_arr = p.generate_predictions()
                        save_datapoint(prob_success_arr, N, W, lat_mean, lat_stddev, itt, auto_rate, idx)
                        idx += 1 
                        #Y[-1].append(numpy.median(prob_success_arr))
                        #X[-1].append(itt)

                #data = []
                #for i in range(len(X)):
                #    data.append((X[i], Y[i]))
                #plot_id = "N_%d_W_%d_latency_%f"%(N, W, lat_mean)
                #plot_wrt_itt(data, labels, "%s.pdf"%plot_id)

if __name__ == "__main__":
    main()
