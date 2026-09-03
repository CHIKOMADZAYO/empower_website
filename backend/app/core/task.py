from collections.abc import Callable

from fastapi import BackgroundTasks


class Task:
    """Queue application work for execution after an HTTP response."""

    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def add_task(
        self,
        func: Callable[..., object],
        *args: object,
        **kwargs: object,
    ) -> None:
        """Add a synchronous or asynchronous callable to the task queue."""
        self.background_tasks.add_task(func, *args, **kwargs)

    
