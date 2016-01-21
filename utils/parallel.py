import multiprocessing as mp


def populate_queue(q, data):
    for datum in data:
        q.put(datum)


def create_queue(data=[]):
    q = mp.JoinableQueue()
    populate_queue(q, data)
    return q


class Worker:
    def __init__(self):
        self.process = None


    def work(self):
        pass


    def start(self):
        self.process = mp.Process(target=self.work)
        self.process.daemon = True
        self.process.start()


    def join(self):
        self.process.join()
