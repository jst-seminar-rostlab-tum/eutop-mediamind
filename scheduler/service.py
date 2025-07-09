from typing import Callable, List, Optional, Any
import uuid
from redis import Redis
from datetime import timedelta, datetime, timezone

from rq_scheduler import Scheduler


class SchedulerService:
    _scheduler: Scheduler
    _redis: Redis

    def __init__(self, redis: Redis):
        self._redis = redis

        self._scheduler = Scheduler(connection=redis)

    def schedule(self, func: Callable, args: Optional[List[Any]]=None) -> None:
        """
        Schedule a task for a single, immediate execution.
        :param func: The function to be executed.
        :param args: Arguments to pass to the function.
        """
        # Add one seccond buffer just in case
        execution_time = datetime.now(timezone.utc) + timedelta(seconds=1)
        self.schedule_at(execution_time, func=func, args=args)

    def schedule_at(self, execution_time: datetime, func: Callable, args: Optional[List[Any]]=None) -> None:
        """
        Schedule a task to run at a specific time.
        :param scheduled_time: The time at which the task should be executed.
        :param func: The function to be executed.
        :param args: Arguments to pass to the function.
        """
        self._scheduler.schedule(
            scheduled_time=execution_time,
            func=func,
            args=args,
            repeat=1,
            interval=1,
        )

    def schedule_periodic(self, id: uuid.UUID, every_seconds: int, func: Callable, args: Optional[List[Any]]=None) -> None:
        """
        Schedule a periodic task.
        :param id: Unique identifier for the task.
        :param every_seconds: Interval in seconds between executions.
        :param func: The function to be executed periodically.
        :param args: Arguments to pass to the function.
        """
        self._scheduler.schedule(
            id=str(id),
            scheduled_time=datetime.now(),
            func=func,
            args=args,
            interval=every_seconds,
            on_failure=fail,
        )

def fail():
    print("porca maddonna")
