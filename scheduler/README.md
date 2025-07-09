# Scheduler

## Getting Started

- Create a virtual environment:
  ```bash
  python -m venv venv
  ```
  Notes:
  - On Windows: Use `python` or `py -3` if you have the Python Launcher
  - On macOS/Linux: Use `python3` if `python` points to Python 2
  - Alternative Windows command: `py -m venv venv`
- Activate the virtual environment:
  - On Windows:
    ```bash
    venv\Scripts\activate
    ```
  - On macOS and Linux:
    ```bash
    source venv/bin/activate
    ```
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Start the project:
    ```bash
    python main.py
    ```

## Scheduling jobs
Job scheduling is relying on the [rq](https://github.com/rq/rq) and 
[rq-scheduler](https://github.com/rq/rq-scheduler) packages.

## Scheduling Jobs
To schedule jobs, you can use the `SchedulerService` class, which is a wrapper 
around the `rq-scheduler` package.

_Note:_ for the scheduler to work, you need to have a Redis server running.

Jobs are simple Python functions, that could take any number of arguments:
```python
def my_function(arg1, arg2):
    # Your job logic here
    print(f"Job executed with arguments: {arg1}, {arg2}")
```

Schedule a job to run immediately:
```python
from app.services.scheduler import SchedulerService

SchedulerService.schedule_job(
    func=my_function,
    args=(arg1, arg2),
)
```

Schedule a job to run at a specific time:
```python
from app.services.scheduler import SchedulerService
from datetime import datetime

SchedulerService.schedule_at(
    execution_time=datetime(2023, 10, 1, 12, 0, 0),
    func=my_function,
    args=(arg1, arg2),
)
```

Schedule a periodic job:
```python
from app.services.scheduler import SchedulerService

SchedulerService.schedule_periodic(
    interval=60,  # Runs every 60 seconds
    func=my_function,
    args=(arg1, arg2),
)
```

Async jobs can also be scheduled, but they need to be wrapped in a synchronous 
function:
```python
from asyncio import get_event_loop

async def my_async_function(arg1, arg2):
    # Your async job logic here
    print(f"Async job executed with arguments: {arg1}, {arg2}")

def my_job(arg1, arg2):
    loop = get_event_loop()
    loop.create_task(my_async_function(arg1, arg2))

# ...

SchedulerService.schedule_job(
    func=my_job,
    args=(arg1, arg2),
)
```

## How does it work?
The job scheduling process is composed of three main components
- The _client_, which decides which job must be scheduled and when (i.e. the 
    FastAPI app);
- The _scheduler_, which is responsible for the actual scheduling of the jobs; and
- The _worker_, which is a mere executor of the scheduled jobs.

```mermaid
sequenceDiagram
    participant Client
    participant Scheduler
    participant Worker

    Client->>Scheduler: scheduled-job queue
    Scheduler->>Worker: queued-job queue
```

The flow is as follows:
1. The client creates a job using the `rq-scheduler` package (see previous section).
   By doing so, the job is added to a Redis queue dedicated to scheduled jobs.
2. The scheduler is a long-running process that checks the Redis queue for 
   scheduled jobs. When it finds a job that is due to be executed, it moves the
    job to another Redis queue, containing jobs that are ready to be executed.
3.  Finally, the worker consumes the jobs from the execution queue and executes them.
