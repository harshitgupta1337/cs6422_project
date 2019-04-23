import time
from numpy.random import poisson
from threading import Thread

class PoissonProcess(Thread):
    def __init__(self, rate, callback):
        super(PoissonProcess, self).__init__()
        self.rate = rate
        self.callback = callback
    
    def run(self):
        while True:
            beta = 1/self.rate
            t = poisson(beta)
            time.sleep(t)
            self.callback()

def callback():
    print ("Callback executing")

if __name__=="__main__":
    p = PoissonProcess(1, callback)
    p.start()

