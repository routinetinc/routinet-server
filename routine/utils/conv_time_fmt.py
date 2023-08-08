from datetime import datetime
from typing import Union
from dateutil.parser import isoparse
from django.utils import timezone

#*---------------------------- 変換に必要な機能 ---------------------------------------------*#

# datetime, ut 端数(秒未満)切捨て関数
def round_datetime_ut(t : Union[float, datetime]) -> Union[int, datetime]:
    if(isinstance(t, datetime)):
        t = t.replace(microsecond = 0)
    elif(isinstance(t, float)):
        t = round(t)
    return t


#*---------------------------- DateTime <-> Other ------------------------------------------*#

# datetime <-> iso8601 (基本形式)
def conv_datetime_iso(t: Union[datetime, str]):
    if(isinstance(t, datetime)):
        t = round_datetime_ut(t)
        t = t.strftime("%Y%m%dT%H%M%S%z")
    elif(isinstance(t, str)):
        t = isoparse(t).strftime("%Y%m%dT%H%M%S%z")
    return t
