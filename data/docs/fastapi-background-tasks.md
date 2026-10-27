---
title: FastAPI Background Tasks
source: https://fastapi.tiangolo.com/tutorial/background-tasks/
---

# Background Tasks in FastAPI

FastAPI provides an easy, built-in way to run tasks in the background after returning an HTTP response.

This capability comes directly from Starlette and is integrated seamlessly with FastAPI's parameter injection.

## What are Background Tasks

In web applications, some operations take significant time to execute but do not produce output needed by the client immediately.

Examples include:
* Sending email notifications after account registration.
* Generating analytics events or tracking user actions.
* Processing or formatting log files.
* Triggering cache invalidations or webhook notifications.

By executing these tasks in the background after sending the response, the API can return immediately with low latency, providing a fast user experience.

## Using BackgroundTasks

To use background tasks, declare a parameter of type `BackgroundTasks` in your path operation function.

Then, call `.add_task()` with your function and any arguments it needs:

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def write_notification(email: str, message: str = ""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}\n"
        email_file.write(content)

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}
```

FastAPI will send the HTTP response `{"message": "Notification sent in the background"}` first, and then execute `write_notification` in the background.

## Dependencies with Background Tasks

You can also use `BackgroundTasks` inside FastAPI dependencies.

This is useful when an authentication or database dependency needs to schedule an audit log or cleanup task that should run after the response is sent:

```python
def write_log(message: str):
    with open("log.txt", "a") as log:
        log.write(message)

def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        message = f"found query: {q}\n"
        background_tasks.add_task(write_log, message)
    return q
```

## Technical Details: Execution Model

FastAPI's `BackgroundTasks` runs tasks in-process:
* If the task is a standard synchronous `def` function, FastAPI runs it in the external thread pool (`anyio.to_thread.run_sync`).
* If the task is an asynchronous `async def` function, FastAPI awaits it directly in the event loop after the response has been sent.

## When to Use Celery or Distributed Queues

Because `BackgroundTasks` runs inside the same process as the FastAPI web server:
* If the server process crashes or restarts, pending in-memory background tasks will be lost.
* Heavy CPU-bound computation or long-running jobs (e.g. video rendering, deep learning model inference) can saturate the server's CPU and memory.

For heavy, mission-critical, or distributed workloads, FastAPI documentation recommends dedicated distributed task queues like **Celery**, **ARQ**, or **RQ** backed by Redis or RabbitMQ.
