import sys
from os import mkdir
from os.path import join, isdir, isfile
from os import listdir
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
import yaml

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

def plot_data(data, labels, outfile_name, x_label):
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
    xtitle = x_label
    plt.xlabel(xtitle, fontsize=14)
    ytitle = "Probability of success"
    plt.ylabel(ytitle, fontsize=14)
    plt.savefig(outfile_name, bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.close(fig)

class Plotter:
    def __init__(self, folderpath):
        self.folderpath = folderpath
        self.unique_vals = {}
        self.datapoints = {}
        self.read_vals()
        self.read_datapoints()

    def read_conf(self, datapoint_folder):
        f = open(join(datapoint_folder, "conf.yaml"))
        doc = yaml.load(f)
        f.close()
        return doc

    def read_data(self, datapoint_folder):
        f = open(join(datapoint_folder, "data.txt"))
        points = []
        for line in f.readlines():
            points.append(float(line))
        f.close()
        return points

    def read_vals(self):
        f = open(join(self.folderpath, "vals.yaml"))
        self.unique_vals = yaml.load(f)
        f.close()

    def form_key(self, conf):
        key=""
        for var in self.unique_vals.keys():
            key += "%s_%s_"%(var, str(conf[var]))
        return key

    def read_datapoints(self):
        dirnames = filter(lambda x: isdir(join(self.folderpath, x)) and x.startswith("datapoint"), listdir(self.folderpath))
        for dirname in dirnames:
            conf = self.read_conf(join(self.folderpath, dirname))
            data = self.read_data(join(self.folderpath, dirname))
            key = self.form_key(conf)
            print ("Adding key = ", key)
            self.datapoints[key] = data

    def plot(self, x_var, line_var):
        other_vars = []
        for var in self.unique_vals.keys():
            if var == x_var or var == line_var:
                pass
            else:
                other_vars.append(var)
        
        print ((other_vars), x_var, line_var)
        
        for N in self.unique_vals["N"]:
            for W in self.unique_vals["W"]:
                for lat_mean in self.unique_vals["lat_mean"]:
                    X = []
                    Y = []
                    labels = []
                    for auto_rate in self.unique_vals["auto_rate"]:
                        X.append([])
                        Y.append([])
                        labels.append("AutoRate = %f"%auto_rate)
                        for itt in self.unique_vals["itt"]:
                            #p = SingleControllerPredictor(N, W, itt, auto_rate, num_trials, lat_mean, lat_stddev)
                            conf = {}
                            conf["N"] = N
                            conf["W"] = W
                            conf["lat_mean"] = lat_mean
                            conf["auto_rate"] = auto_rate
                            conf["itt"] = itt
                            key = self.form_key(conf)
                            prob_success_arr = self.datapoints[key]
                            Y[-1].append(numpy.median(prob_success_arr))
                            X[-1].append(itt)

                    data = []
                    for i in range(len(X)):
                        data.append((X[i], Y[i]))
                    plot_id = "N_%d_W_%d_latency_%f"%(N, W, lat_mean)
                    plot_data(data, labels, "%s.png"%plot_id, "Inter transaction time")

        for N in self.unique_vals["N"]:
            for itt in self.unique_vals["itt"]:
                for lat_mean in self.unique_vals["lat_mean"]:
                    X = []
                    Y = []
                    labels = []
                    for auto_rate in self.unique_vals["auto_rate"]:
                        X.append([])
                        Y.append([])
                        labels.append("AutoRate = %f"%auto_rate)
                        for W in self.unique_vals["W"]:
                            conf = {}
                            conf["N"] = N
                            conf["W"] = W
                            conf["lat_mean"] = lat_mean
                            conf["auto_rate"] = auto_rate
                            conf["itt"] = itt
                            key = self.form_key(conf)
                            prob_success_arr = self.datapoints[key]
                            Y[-1].append(numpy.median(prob_success_arr))
                            X[-1].append(W)

                    data = []
                    for i in range(len(X)):
                        data.append((X[i], Y[i]))
                    plot_id = "N_%d_itt_%.1f_latency_%f"%(N, itt, lat_mean)
                    plot_data(data, labels, "%s.png"%plot_id, "Write quorum")

if __name__ == "__main__":
    plotter = Plotter("./dump")
    plotter.plot("itt", "auto_rate")
