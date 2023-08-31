<<<<<<< HEAD
from datetime import datetime
from django.db import models
from rest_framework import serializers

class CustomModels:
    class TimeStringField(models.CharField):
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
                    dow_list.append(f'{i}') 
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

class CustomSerializers:
    class TimeStringField(serializers.Field):
        def to_internal_value(self, value: str):
            if len(value) != 11:
                raise serializers.ValidationError("Expected format: 'HHMMSS+TZ'")
            try:
                time_str = value[:6]
                tz_str = value[6:]
                hours = int(time_str[:2])
                minutes = int(time_str[2:4])
                seconds = int(time_str[4:])
            except ValueError:
                raise serializers.ValidationError("Expected format: 'HHMMSS+TZ'")
            datetime_obj = datetime(1900, 1, 1, hours, minutes, seconds, 0)
            return datetime_obj.strftime('%H%M%S') + tz_str
        def to_representation(self, value: datetime):
            time_str = value.strftime('%H%M%S')
            tz_str = value.strftime('%z')
=======
from datetime import datetime, timezone, timedelta
from django.db import models
from rest_framework import serializers

class CustomModels:
    class TimeStringField(models.CharField):
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
                    dow_list.append(f'{i}') 
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

class CustomSerializers:
    class ISOTimeField(serializers.Field):
        def to_internal_value(self, value: str):
            if not (len(value) == 20 and value[8] == 'T'):
                raise serializers.ValidationError("Expected format: 'YYYYMMDDThhmmss+TZ'")
            try:
                year = int(value[:4])
                month = int(value[4:6])
                day = int(value[6:8])
                hours = int(value[9:11])
                minutes = int(value[11:13])
                seconds = int(value[13:15])
                tz_hours = int(value[15:18])
                tz_minutes = int(value[18:20])
                tz_info = timezone(timedelta(hours=tz_hours, minutes=tz_minutes))
            except ValueError:
                raise serializers.ValidationError("Expected format: 'YYYYMMDDThhmmss+TZ'")
            datetime_obj = datetime(year, month, day, hours, minutes, seconds, tzinfo=tz_info)
            return datetime_obj
        def to_representation(self, value: datetime):
            time_str = value.strftime('%Y%m%dT%H%M%S')
            tz_str = value.strftime('%z')
            return time_str + tz_str
           
    class TimeStringField(serializers.Field):
        def to_internal_value(self, value: str):
            if len(value) != 11:
                raise serializers.ValidationError("Expected format: 'HHMMSS+TZ'")
            try:
                time_str = value[:6]
                tz_str = value[6:]
                hours = int(time_str[:2])
                minutes = int(time_str[2:4])
                seconds = int(time_str[4:])
            except ValueError:
                raise serializers.ValidationError("Expected format: 'HHMMSS+TZ'")
            datetime_obj = datetime(1900, 1, 1, hours, minutes, seconds, 0)
            return datetime_obj.strftime('%H%M%S') + tz_str
        def to_representation(self, value: datetime):
            time_str = value.strftime('%H%M%S')
            tz_str = value.strftime('%z')
>>>>>>> dev
            return time_str + tz_str