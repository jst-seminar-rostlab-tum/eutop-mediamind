from typing import Callable, List, Optional, Any
from redis import Redis
from datetime import timedelta, datetime, timezone

from rq_scheduler import Scheduler


class SchedulerService:
    _scheduler: Optional[Scheduler] = None
    _redis: Optional[Redis]= None

    @staticmethod
    def _get_scheduler() -> Scheduler:
        if SchedulerService._scheduler is None:
            raise RuntimeError("Scheduler not initialized")
        return SchedulerService._scheduler

    @staticmethod
    def init_scheduler(redis: Redis) -> None:
        SchedulerService._redis = redis
        SchedulerService._scheduler = Scheduler(connection=redis, queue_name="q2")

    @staticmethod
    def schedule(func: Callable, args: Optional[List[Any]]=None) -> None:
        """
        Schedule a task for a single, immediate execution.
        :param func: The function to be executed.
        :param args: Arguments to pass to the function.
        """
        # Add one seccond buffer just in case
        execution_time = datetime.now(timezone.utc) + timedelta(seconds=1)
        SchedulerService.schedule_at(execution_time, func=func, args=args)

    @staticmethod
    def schedule_at(execution_time: datetime, func: Callable, args: Optional[List[Any]]=None) -> None:
        """
        Schedule a task to run at a specific time.
        :param scheduled_time: The time at which the task should be executed.
        :param func: The function to be executed.
        :param args: Arguments to pass to the function.
        """
        s = SchedulerService._get_scheduler()
        s.schedule(
            scheduled_time=execution_time,
            func=func,
            args=args,
            repeat=1,
            interval=1,
        )

    @staticmethod
    def schedule_periodic(every_seconds: int, func: Callable, args: Optional[List[Any]]=None) -> None:
        """
        Schedule a periodic task.
        :param every_seconds: Interval in seconds between executions.
        :param func: The function to be executed periodically.
        :param args: Arguments to pass to the function.
        """
        s = SchedulerService._get_scheduler()
        s.schedule(
            scheduled_time=datetime.now(),
            func=func,
            args=args,
            interval=every_seconds,
        )
