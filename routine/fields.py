from datetime import datetime
from django.utils import timezone
from django.utils.timezone import localtime
from . import models

class TimeField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs['default'] = '000000+0000'
        super().__init__(*args, **kwargs)
    def from_db_value(self, value: datetime, expression=None, connection=None):
        if value is None:
            return value
        return value.strftime('%H%M%S%z')
    def to_python(self, value: datetime,  expression=None, connection=None):
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return value.strftime('%H%M%S%z')
    def get_prep_value(self, value: datetime,  expression=None, connection=None):
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return value.strftime('%H%M%S%z')
    
a = 1
    
