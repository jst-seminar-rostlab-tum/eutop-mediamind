from collections.abc import Callable
from datetime import datetime
from redis import Redis
from rq import Queue, Repeat

class _Scheduler:

    def __init__(self, redis: Redis):
        self._redis = redis
        self._queues = {}


    def schedule(self, queue: str, task: Callable, *args, **kwargs):
        return self._get_queue(queue).enqueue(task, args, kwargs)

    def schedule_repeated(self, queue: str, repeat: Repeat, task: Callable, *args, **kwargs):
        return self._get_queue(queue).enqueue(task, args, kwargs, repeat=repeat)

    def schedule_at(self, queue: str, when: datetime, task: Callable , *args, **kwargs):
        return self._get_queue(queue).enqueue_at(when, task, args, kwargs)

    def _get_queue(self, queue: str) -> Queue:
        if queue not in self._queues:
            self._queues[queue] = Queue(queue, connection=self._redis)
        return self._queues[queue]

class SchedulerService:
    _scheduler = None

    @staticmethod
    def _get_scheduler() -> _Scheduler:
        global _scheduler
        if _scheduler is None:
            raise RuntimeError("Scheduler not initialized. Call init_scheduler first.")
        return _scheduler

    # Initialize the scheduler with a Redis connection
    @staticmethod
    def init_scheduler(redis: Redis):
        global _scheduler
        _scheduler = _Scheduler(redis)

    @staticmethod
    def schedule(queue: str, task: Callable, *args, **kwargs):
        return SchedulerService._get_scheduler().schedule(queue, task, args, kwargs)

    @staticmethod
    def schedule_repeated(queue: str, repeat: Repeat, task: Callable, *args, **kwargs):
        return SchedulerService._get_scheduler().schedule_repeated(queue, repeat, task, args, kwargs)

    @staticmethod
    def schedule_at(queue: str, when: datetime, task: Callable, *args, **kwargs):
        return SchedulerService._get_scheduler().schedule_at(queue, when, task, args, kwargs)
