import requests
from pprint import pprint
import json

app_id = 'deanwang8-410c4a97-3be0-44fa'
app_key = '570e63e5-b3c5-4302-9eaa-d87b748c30bb'

auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"

# 讓使用者輸入車次號碼和上車地點
train_number = input("請輸入公車車次號碼：")
boarding_location = input("請輸入查詢縣市：")

# 動態生成查詢車次的 URL
url = f"https://tdx.transportdata.tw/api/basic/v2/Bus/StopOfRoute/City/{boarding_location}/{train_number}?%24top=30&%24format=JSON"

class Auth():

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        content_type = 'application/x-www-form-urlencoded'
        grant_type = 'client_credentials'

        return {
            'content-type': content_type,
            'grant_type': grant_type,
            'client_id': self.app_id,
            'client_secret': self.app_key
        }

class data():

    def __init__(self, app_id, app_key, auth_response):
        self.app_id = app_id
        self.app_key = app_key
        self.auth_response = auth_response

    def get_data_header(self):
        auth_JSON = json.loads(self.auth_response.text)
        access_token = auth_JSON.get('access_token')

        return {
            'authorization': 'Bearer ' + access_token
        }

if __name__ == '__main__':
    try:
        a = Auth(app_id, app_key)
        auth_response = requests.post(auth_url, a.get_auth_header())
        d = data(app_id, app_key, auth_response)
        data_response = requests.get(url, headers=d.get_data_header())
    except:
        print("身份驗證失敗或查詢車次資訊錯誤")

    print(auth_response)
    pprint(auth_response.text)
    print(data_response)
    pprint(data_response.text)

