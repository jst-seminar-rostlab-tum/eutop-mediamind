"""
Run also the scheduler, as separate thread with:
rqscheduler -i <refresh_interval> [-v]

"""
from redis import Redis
from rq import Worker

redis = Redis()

worker = Worker(['q2'], connection=redis)

if __name__ == '__main__':
    worker.work(with_scheduler=True, burst=False)
