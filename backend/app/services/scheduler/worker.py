from redis import Redis
from rq_scheduler import Scheduler
from rq import Worker
from multiprocessing import Process

def _start_worker(redis: Redis, queue: str) -> None:
    worker = Worker(queues=[queue], connection=redis)
    worker.work(burst=False) 

def _start_scheduler(redis: Redis) -> None:
   scheduler = Scheduler(connection=redis, interval=30)
   scheduler.run()  

def start(redis: Redis, queue: str) -> None:
    worker_process = Process(target=_start_worker, kwargs={"redis": redis, "queue": queue})
    worker_process.start()

    scheduler_process = Process(target=_start_scheduler, kwargs={"redis": redis})
    scheduler_process.start()


if __name__ == "__main__":
    from fastapi import FastAPI
    app = FastAPI()

    start(Redis(), "default")


