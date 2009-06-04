from celery import discovery
from UserDict import UserDict


class NotRegistered(Exception):
    """The task is not registered."""


class AlreadyRegistered(Exception):
    """The task is already registered."""


class TaskRegistry(UserDict):
    """Site registry for tasks."""

    AlreadyRegistered = AlreadyRegistered
    NotRegistered = NotRegistered

    def __init__(self):
        self.data = {}

    def autodiscover(self):
        """Autodiscovers tasks using :func:`celery.discovery.autodiscover`."""
        discovery.autodiscover()

    def register(self, task, task_name=None):
        """Register a task in the task registry.

        Task can either be a regular function, or a class inheriting
        from :class:`celery.task.Task`.

        :keyword task_name: By default the :attr:`Task.name` attribute on the
            task is used as the name of the task, but you can override it
            using this option.

        :raises AlreadyRegistered: if the task is already registered.

        """
        is_class = hasattr(task, "run")

        if not task_name:
            task_name = getattr(task, "name")

        if task_name in self.data:
            raise self.AlreadyRegistered(
                    "Task with name %s is already registered." % task_name)

        if is_class:
            self.data[task_name] = task() # instantiate Task class
        else:
            task.name = task_name
            task.type = "regular"
            self.data[task_name] = task

    def unregister(self, task_name):
        """Unregister task by name.

        :param task_name: name of the task to unregister.

        :raises NotRegistered: if the task has not been registered.

        """
        if hasattr(task_name, "run"):
            task_name = task_name.name
        if task_name not in self.data:
            raise self.NotRegistered(
                    "Task with name %s is not registered." % task_name)
        del self.data[task_name]

    def get_all(self):
        """Get all task types."""
        return self.data

    def filter_types(self, type):
        """Return all tasks of a specific type."""
        return dict([(task_name, task)
                        for task_name, task in self.data.items()
                            if task.type == type])

    def get_all_regular(self):
        """Get all regular task types."""
        return self.filter_types(type="regular")

    def get_all_periodic(self):
        """Get all periodic task types."""
        return self.filter_types(type="periodic")

    def get_task(self, task_name):
        """Get task by name."""
        return self.data[task_name]

"""
.. data:: tasks

    The global task registry.

"""
tasks = TaskRegistry()
