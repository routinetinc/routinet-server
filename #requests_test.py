import requests
import json
BLUE = '\033[36m'
END = '\033[0m'

# テスト方法: url, json_data を適した値にし、app.py を実行中に新たなターミナル (別のデスクトップを立ち上げても良い) で requests_test.py を実行.
# requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0) の エラーは json 由来ではないため、アプリ側のエラーを参照.


# リクエスト先 URL
url = 'http://127.0.0.1:8000/feed/sns/feed/task/comment/'
request_methods = {0: 'get', 1: 'post', 2: 'patch', 3: 'delete'} 
request_method  = request_methods[0]

# JSON 形式のデータ(リクエスト用). 変数 json_data の格納値にドキュメントの {'data': data_value } 全体をコピペする.
json_data = {
	
}


# アクセス
headers = {'Content-Type': 'application/json'}
if(request_method == request_methods[0]):
  	response = requests.get(url)
elif(request_method == request_methods[1]):
  	response = requests.post(url, json=json_data, headers=headers)
elif(request_method == request_methods[2]):
  	response = requests.patch(url, json=json_data, headers=headers)
elif(request_method == request_methods[3]):
		response = requests.delete(url, json=json_data, headers=headers)
else:
  	pass

print(f'{BLUE}url         ={END} {url}')
print(f'{BLUE}headers     ={END} {response.request.headers}')
print(f'{BLUE}body        ={END} {response.request.body}')
print(f'{BLUE}method      ={END} {response.request.method}')
res_data = response.json()
print(res_data)
print(f'{BLUE}status_code ={END} {res_data["status_code"]}')
print(f'{BLUE}res_data    ={END} {res_data["data"]}')

