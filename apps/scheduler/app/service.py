import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, List, Optional

from redis import Redis
from rq_scheduler import Scheduler


class SchedulerService:
    _scheduler: Scheduler
    _redis: Redis

    def __init__(self, redis: Redis):
        self._redis = redis

        self._scheduler = Scheduler(connection=redis)

    def schedule(
        self,
        func: Callable,
        args: Optional[List[Any]] = None,
    ) -> None:
        """
        Schedule a task for a single, immediate execution.
        :param func: The function to be executed.
        :param args: Arguments to pass to the function.
        """
        # Add one seccond buffer just in case
        execution_time = datetime.now(timezone.utc) + timedelta(seconds=1)
        self.schedule_at(execution_time, func=func, args=args)

    def schedule_at(
        self,
        execution_time: datetime,
        func: Callable,
        args: Optional[List[Any]] = None,
    ) -> None:
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

    def schedule_periodic(
        self,
        id: uuid.UUID,
        every_seconds: int,
        func: Callable,
        args: Optional[List[Any]] = None,
    ) -> None:
        """
        Schedule a periodic task.
        :param id: Unique identifier for the task.
        :param every_seconds: Interval in seconds between executions.
        :param func: The function to be executed periodically.
        :param args: Arguments to pass to the function.
        """
        self._scheduler.schedule(
            id=str(id),
            scheduled_time=datetime.now(timezone.utc),
            func=func,
            args=args,
            interval=every_seconds,
        )

    def schedule_daily_at_times(
        self,
        id: uuid.UUID,
        times: List[str],  # List of times in "HH:MM" format
        func: Callable,
        args: Optional[List[Any]] = None,
    ) -> None:
        """
        Schedule a task to run daily at specific times.
        :param id: Unique identifier for the task.
        :param times: List of times in "HH:MM" format
                     (e.g., ["10:00", "16:00", "20:00"])
        :param func: The function to be executed.
        :param args: Arguments to pass to the function.
        """
        # Calculate seconds in a day
        seconds_in_day = 24 * 60 * 60
        
        # Get current time
        now = datetime.now(timezone.utc)
        
        # Schedule for each time
        for i, time_str in enumerate(times):
            try:
                hour, minute = map(int, time_str.split(':'))
                
                # Calculate next occurrence of this time today
                target_time = now.replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
                
                # If the time has already passed today, schedule for tomorrow
                if target_time <= now:
                    target_time += timedelta(days=1)
                
                # Schedule with daily interval, using unique ID for each time
                unique_id = f"{id}_{i}"
                self._scheduler.schedule(
                    id=unique_id,
                    scheduled_time=target_time,
                    func=func,
                    args=args,
                    interval=seconds_in_day,  # Repeat every 24 hours
                )
            except ValueError:
                raise ValueError(
                    f"Invalid time format: {time_str}. Expected HH:MM format."
                )
