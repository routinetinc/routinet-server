from datetime import datetime
from django.db import models
from rest_framework import serializers

#* ------------------------ models ------------------------------*#

class TimeField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs['default'] = '000000+0000'
        super().__init__(*args, **kwargs)
    def from_db_value(self, value: datetime, expression=None, connection=None):
        """ value: (e.g.) datetime.now(jst_tz), localtime(timezone.now()) """
        if isinstance(value, str):
            return value        
        if value is None:
            return value
        return value.strftime('%H%M%S%z')
    def to_python(self, value: datetime,  expression=None, connection=None):
        """ value: (e.g.) datetime.now(jst_tz), localtime(timezone.now()) """
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return value.strftime('%H%M%S%z')
    def get_prep_value(self, value: datetime,  expression=None, connection=None):
        """ value: (e.g.) datetime.now(jst_tz), localtime(timezone.now()) """
        if isinstance(value, str):
            return value
        if value is None:
            return value
        return value.strftime('%H%M%S%z')
    
class DOWField(models.IntegerField):
    def dow_from_list_to_int(self, dow_list: list[str]) -> int:
        dow_int = 0
        for l in dow_list:
            dow_int += 1 << int(l)
        return dow_int
    def dow_from_int_to_list(self, dow_int: int) -> list[str]:
        dow_list = []
        i = 0
        while dow_int > 0:
            if(dow_int % 2 != 0):
                dow_list.append(f"{i}") 
            i += 1
            dow_int >>= 1
        return dow_list
    def from_db_value(self, value: int, expression=None, connection=None):
        if value is None:
            return value
        return self.dow_from_int_to_list(value)
    def to_python(self, value: int, expression=None, connection=None):
        if value is None:
            return value
        return self.dow_from_int_to_list(value)
    def get_prep_value(self, value: list[str], expression=None, connection=None):
        if value is None:
            return value
        return self.dow_from_list_to_int(value)


#* ----------------------- serializers -------------------------------------*#

class TimeStringField(serializers.Field):
    def to_internal_value(self, value: str):
        if len(value) != 13:
            raise serializers.ValidationError("Invalid time format. Expected format: 'HHMMSS+TZ'")
        try:
            time_str = value[:6]
            tz_str = value[6:]
            hours = int(time_str[:2])
            minutes = int(time_str[2:4])
            seconds = int(time_str[4:])
        except ValueError:
            raise serializers.ValidationError("Invalid time format. Expected format: 'HHMMSS+TZ'")
        datetime_obj = datetime(1900, 1, 1, hours, minutes, seconds, 0, tz_str)
        return datetime_obj.strftime("%H%M%S%z")
    def to_representation(self, value: datetime):
        return value.strftime("%H%M%S%z")