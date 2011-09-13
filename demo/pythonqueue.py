#import multiprocessing as mp

import threading as mp
Process = mp.Thread

import time

from Queue import Queue

class Runner(Process):
    def __init__(self, queue, server):
        super(Runner,self).__init__()
        self.queue = queue
        self.server = server
    def run(self):
        while True:
            ans = self.queue.get()
            if ans == 'stop':
                break
            self.server.put(ans*2)


for n in xrange(100):
    start = time.time()

    queues = [(Queue(), Queue()) for  _ in xrange(n)]
    threads = [Runner(*queuepair) for queuepair in queues]
    for thread in threads:
        thread.start()

    for i in xrange(2000):
        for send,recv in queues:
            send.put(i)
            j = recv.get()
            assert i*2 == j
        #print '.',

    for send,recv in queues:
        send.put('stop')

    for thread in threads:
        thread.join()

    end = time.time()
    print n, end-start
