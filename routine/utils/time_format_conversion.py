from time import time
from datetime import datetime, date, timedelta
from typing import Final, Union
import pytz
jst_tz: Final = pytz.timezone('Asia/Tokyo')


#*------------------------------- 変換に必要な機能 -------------------------------------------------*#

# datetime, ut 端数(秒未満)切捨て関数
def round_datetime_ut(t : Union[float, datetime]) -> Union[int, datetime]:
    if(isinstance(t, datetime)):
        t = t.replace(microsecond = 0)
    elif(isinstance(t, float)):
        t = round(t)
    return t

# iso8601 から 年, 月, 日, 時, 分, 秒を抽出
def extract_elem_from_iso(iso: str) -> dict[int]:
    iso = iso.replace("/", "")  # 文字列時間にも対応できるように 
    iso = iso.replace(" ", "")  # 同上
    iso = iso.replace("-", "")  # ∴ TZ は、参照不可。
    iso = iso.replace("+", "")  # ∴ TZ は、参照不可。
    iso = iso.replace(":", "")
    iso = iso.replace("T", "")
    iso += "0000000000"         # 文字列時間などにも対応するよう 0 埋め
    dt_elem = {
        "year": int(iso[:4]),
        "month": int(iso[4:6]),
        "day": int(iso[6:8]),
        "hour": int(iso[8:10]),
        "minute": int(iso[10:12]),
        "second": int(iso[12:14]),
    }
    return dt_elem


#*------------------------------------- DateTime <-> Other ---------------------------------------------------*#

#? tzinfo = jst_tz とすると、tz = +09:19 となるので、 jst_tz.localize() を使用
#? t.astimezone(jst_tz) とすると、 +08:00 されるので、 jst_tz.localize() を使用

# datetime <-> ut 
def trans_datetime_ut(t : Union[datetime, int]) -> Union[datetime, int]:
    t = round_datetime_ut(t)
    if(isinstance(t, datetime)):
        t = datetime.timestamp(t)
        t = round(t) #変換後に生じる端数切捨て
    elif(isinstance(t, int)):
        t = datetime.fromtimestamp(t, jst_tz)
    return t

# datetime <-> iso8601
def trans_datetime_iso(t: Union[datetime, str], is_basic_format: bool = True):
    """ The 2nd arg is used in only datetime -> iso """
    global jst_tz
    if(isinstance(t, datetime)):
        t = round_datetime_ut(t)
        t = t.strftime('%Y%m%dT%H%M%S%z') if(is_basic_format) else t.strftime('%Y-%m-%dT%H:%M:%S%z')
    elif(isinstance(t, str)):
        t = extract_elem_from_iso(t)
        t = datetime(t["year"], t["month"], t["day"], t["hour"], t["minute"], t["second"], 0)
        t = jst_tz.localize(t)
    return t