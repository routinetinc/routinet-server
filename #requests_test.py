import requests
import json

# テスト方法: url, json_data を適した値にし、app.py を実行中に新たなターミナル (別のデスクトップを立ち上げても良い) で requests_test.py を実行.
# requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0) の エラーは json 由来ではないため、アプリ側のエラーを参照.


# リクエスト先 URL
url = "http://127.0.0.1:8000/routine/routine/"
# リクエストメソッド: get = 0, post = 1, patch = 2, delete = 3
request_param = 1

# JSON 形式のデータ(リクエスト用). 変数 json_data の格納値にドキュメントの {"data": data_value } 全体をコピペする.
json_data = {
	"data": {
		"dow": ["0", "1", "4"],  # // 月曜を　"0"　とし連番で定義。
		"start_time": "00:00:00",  # // iso基本形式をもじった hh, mm, ss, tz のみの情報をもつ
		"end_time": "00:00:00",  # // iso基本形式をもじった hh, mm, ss, tz のみの情報をもつ
		"title": "foo", 
		"subtitle": "baa",  
		"public": True,
		"notification": True,
		"icon": "a"
	}
}

# アクセス
if(request_param == 0):
  	response = requests.get(url)
elif(request_param == 1):
  	response = requests.post(url, json=json_data)
elif(request_param == 2):
  	response = requests.patch(url, json=json_data)
elif(request_param == 3):
		response = requests.delete(url)
else:
  	pass

res_data = response.json()
print(res_data)
