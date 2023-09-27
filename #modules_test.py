# django.setup() 依存先環境変数値の設定. 
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'kgavengers.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kgavengers.settings')

# Django アプリケーションを初期化しロード
import django
django.setup()
 

#*----------------------- (以下の部分にテストを記述) ---------------------------------*#

from routine.fields import CustomModels
from datetime import datetime
import pytz
from django.utils import timezone
from django.utils.timezone import localtime
from routine.utils.conv_time_fmt import *
RED = '\033[91m'
END = '\033[0m'
jst_tz = pytz.timezone('Asia/Tokyo')

if __name__ == '__main__':
    # routine.fields.TimeField に関するテスト
    try:
        time_f: CustomModels.TimeStringField = CustomModels.TimeStringField()
        # hhmmss+tz の形式で現在時刻が表示されるかを timezone 型経由でテスト
        print(time_f.from_db_value(localtime(timezone.now())))
        # datetime 型経由で from_db_value, to_python, get_prep_value をテスト
        print(time_f.from_db_value(datetime.now(jst_tz)))
        print(time_f.to_python(datetime.now(jst_tz)))
        print(time_f.get_prep_value(datetime.now(jst_tz)))
    except Exception as e:
        print(f'{RED}{e}{END}; generated during routin.fields.TimeField test')
    finally:
        print()
    # routine.fields.DOWField に関するテスト
    try:
        dow_f: CustomModels.DOWField = CustomModels.DOWField()
        # 引数 b1000101 -> ['0', '2', '6'] となるかをテスト
        print(dow_f.dow_from_int_to_list(int('1000101', 2)))
        # 引数 ['0', '2', '6'] -> b1000101 となるかをテスト
        print(f"b{dow_f.dow_from_list_to_int(['0', '2', '6']):07b}")
        # from_db_value, to_python, get_prep_value をテスト
        print(dow_f.from_db_value(int('1000101', 2)))
        print(dow_f.from_db_value(int('1000101', 2)))
        print(f"b{dow_f.get_prep_value(['0', '2', '6']):07b}")
    except Exception as e:
        print(f'{RED}{e}{END}; generated during routin.fields.DOWField test')  
    finally:
        print()
    # routine.utils.conv_time_fmt に関するテスト
    try:
        dt  = timezone.now()
        dt_jst = jst_tz.normalize(dt.astimezone(jst_tz))  # 日本標準時に変換した後、正規化(TZ変更に伴う日時のズレの修正など)
        dt_jst = round_datetime_ut(dt_jst)
        print(f'dt <--> iso | {dt_jst} <--> {conv_datetime_iso(dt_jst)}')
    except Exception as e:
        print(f'{RED}{e}{END}; generated during routine.utils.conv_time_fmt test')  
    finally:
        print()


