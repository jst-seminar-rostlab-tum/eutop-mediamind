"""
Run also the scheduler, as separate thread with:
rqscheduler -i <refresh_interval> [-v]

"""
from redis import Redis
from rq import Worker
from rq_scheduler import Scheduler
from multiprocessing import Process

def start_scheduler(redis: Redis, interval: int = 60):
    scheduler = Scheduler(connection=redis, interval=interval)
    scheduler.run(burst=False)

def main():
    # TODO pass redis connection arguments
    # TODO make queue names and scheduler interval configurable
    redis = Redis()

    # Start scheduler
    scheduler = Process(target=start_scheduler, args=[redis, 10])
    scheduler.start()
    
    # Start worker
    worker = Worker(['q2'], connection=redis)

    worker.work(with_scheduler=True, burst=False)


if __name__ == '__main__':
    main()
