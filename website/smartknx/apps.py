from django.apps import AppConfig
import os
from general_utilities.communication import rt_sync


class SmartknxConfig(AppConfig):
    name = 'smartknx'
   
    def ready(self):
        assert os.environ.get('RUN_MAIN', None) != 'true', "start server with --noreload"
        rt_sync.run_in_thread()