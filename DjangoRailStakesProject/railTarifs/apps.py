from django.apps import AppConfig


class RailtarifsConfig(AppConfig):
    name = 'railTarifs'
    
    def ready(self):
            from . import signals