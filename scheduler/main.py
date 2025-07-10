from redis import Redis, from_url as redis_from_url
from rq_scheduler import Scheduler
from rq import Worker
from multiprocessing import Process
from service import SchedulerService
from job import schedule_jobs
from config import Config
import logging

logger = logging.getLogger(__name__)


def _start_worker(redis: Redis, queue: str) -> None:
    logger.info(f"Starting worker for queue: {queue}")
    worker = Worker(queues=[queue], connection=redis)
    worker.work(burst=False) 

def _start_scheduler(redis: Redis, interval: int) -> None:
   logger.info("Starting scheduler...")
   scheduler = Scheduler(connection=redis, interval=interval)
   scheduler.run()  

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    cfg = Config()

    redis = redis_from_url(cfg.REDIS_URL)
    redis.ping()  # Check if Redis is reachable
    logger.info(f"Connected to Redis at {cfg.REDIS_URL}")

    service = SchedulerService(redis)

    schedule_jobs(service, cfg)
    logger.info("Jobs scheduled successfully.")

    scheduler_process = Process(target=_start_scheduler, kwargs={"redis": redis, "interval": cfg.SCHEDULER_INTERVAL})
    scheduler_process.start()

    _start_worker(redis, cfg.QUEUE_NAME)

if __name__ == "__main__":
    main()
