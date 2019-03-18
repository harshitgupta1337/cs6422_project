import numpy as np

class ControllerServerLatencyDist:
    seq_no = 0
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev
        self.random_gen = np.random.RandomState(self.seq_no)

        self.seq_no += 1

    def sample(self, n=1):
        s = self.random_gen.normal(self.mean, self.stddev, n)
        return s
