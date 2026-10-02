from django.apps import AppConfig


class LeavesConfig(AppConfig):
    name = 'leaves'

    def ready(self):
        from . import signals  # noqa: F401