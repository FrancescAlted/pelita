#import multiprocessing as mp

import threading as mp
Process = mp.Thread

import time

from Queue import Queue

from pelita.messaging import Actor, actor_of, Request, DispatchingActor, expose

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

class ActorRunner(Actor):
    def on_receive(self, message):
        if message == "stop":
            self.ref.stop()
        else:
            self.ref.reply(message*2)


class ActorRunnerD(DispatchingActor):
    @expose
    def double(self, value):
        self.ref.reply(value * 2)

dispatching = False

for n in xrange(100):
    start = time.time()

    if dispatching:
        runners = [actor_of(ActorRunnerD) for _ in xrange(n)]
    else:
        runners = [actor_of(ActorRunner) for _ in xrange(n)]

    for runner in runners:
        runner.start()

    for i in xrange(2000):
        if dispatching:
            for runner in runners:
                j = runner.query("double", [i]).get()
                assert i*2 == j
        else:
            for runner in runners:
                req = Request()
                runner.put(i, channel=req)
                j = req.get()
                assert i*2 == j

        #print '.',

    for runner in runners:
        runner.put('stop')

    end = time.time()
    print n, end-start
