from django.test import TestCase, Client, override_settings
import json
import time


@override_settings(
    ADMIN_SECRET_KEY="37BF3842F53E4E24B2950106625E3763",
    CODE_DATA_REPOSITORY_URL=None,
    ASYNC_DATA_REPOSITORY_URL=None,
    MONGO_REPOSITORY_URL=None,
    DATADOG_API_KEY=None,
    DATADOG_APP_KEY=None
)
class MyTest(TestCase):
    BASE_URL = "http://127.0.0.1:8000/"
    FIND_JSON_DIFF_CODE = """
import json
import time
from django.http import HttpResponse
import traceback

def find_json_diff(json1, json2):
    # 引数として2つのJSONオブジェクトを受け取り、差分を計算して返す関数です。
    
    diff = {}

    # JSONオブジェクトを比較して差分を取得する
    for key in json1:
        if key not in json2:
            diff[key] = json1[key]
        elif json1[key] != json2[key]:
            if isinstance(json1[key], dict) and isinstance(json2[key], dict):
                nested_diff = find_json_diff(json1[key], json2[key])
                if nested_diff:
                    diff[key] = nested_diff
            else:
                diff[key] = json1[key]

    for key in json2:
        if key not in json1:
            diff[key] = json2[key]

    time.sleep(3) #重たい処理
    return diff

def main(req):
    try:
        data = json.loads(req.body)

        diff_result = find_json_diff(data["json1"], data["json2"])
        return HttpResponse(json.dumps(diff_result, ensure_ascii=False), content_type="application/json")
    except Exception as e:
        return HttpResponse(traceback.format_exc(), status=400)

response = main(request)
    """
    json1 = {
        "name": "John",
        "age": 30,
        "address": {
                "street": "123 Main St",
                "city": "New York"
        }
    }

    json2 = {
        "name": "John",
        "age": 35,
        "address": {
                "street": "123 Main St",
                "city": "Los Angeles"
        },
        "phone": "555-1234"
    }
    FIND_JSON_DIFF_DATA = json.dumps(
        {"json1": json1, "json2": json2}, ensure_ascii=False).encode('utf-8')

    def set_up(self):
        self.client = Client()

    def test_exec_input(self):
        #  POSTされたPythonのコードを同期実行するテスト(inputあり)

        response = self.client.post(
            self.BASE_URL + "api/exec_input/", json.dumps(
                {"code": self.FIND_JSON_DIFF_CODE, "json1": self.json1, "json2":  self.json2}, ensure_ascii=False).encode('utf-8'), "application/json")

        result = json.loads(response.content)
        json_diff = {
            "age": 30,
            "address": {"city": "New York"},
            "phone": "555-1234"
        }
        self.assertEqual(result, json_diff)
        self.assertEqual(response.status_code, 200)

    def test_create_api_without_auth(self):
        # 認証なしでAPIを作成するテスト
        response = self.client.post(
            self.BASE_URL + "admin/api_nocheck/find_json_diff/", self.FIND_JSON_DIFF_CODE, "plain/text")
        self.assertEqual(response.status_code, 401)

    def test_create_api(self):
        # 認証情報を設定してAPIを作成するテスト
        from django.conf import settings
        # 認証情報を設定
        auth_headers = {
            'HTTP_AUTHORIZATION': settings.ADMIN_SECRET_KEY,
        }

        response = self.client.post(
            self.BASE_URL + "admin/api_nocheck/find_json_diff/", self.FIND_JSON_DIFF_CODE, "plain/text", **auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_exec_api(self):
        # APIを同期実行するテスト

        response = self.client.post(
            self.BASE_URL + "api/exec/find_json_diff/", self.FIND_JSON_DIFF_DATA, "application/json")

        result = json.loads(response.content)
        json_diff = {
            "age": 30,
            "address": {"city": "New York"},
            "phone": "555-1234"
        }
        self.assertEqual(result, json_diff)
        self.assertEqual(response.status_code, 200)

    def test_exec_async_save_api(self):
        # APIを非同期実行するテスト
        response = self.client.post(
            self.BASE_URL + "api/exec_async_save/find_json_diff/", self.FIND_JSON_DIFF_DATA, "application/json")

        result = json.loads(response.content)

        result_id = result["result_id"]

        for i in range(0, 10):
            response = self.client.get(
                self.BASE_URL + "api/exec_async_result/"+result_id)
            if response.status_code == 200:
                break
            time.sleep(1)  # 処理が終わるまでポーリングして待つ

        result = json.loads(response.content)
        json_diff = {
            "age": 30,
            "address": {"city": "New York"},
            "phone": "555-1234"
        }
        self.assertEqual(result, json_diff)
        self.assertEqual(response.status_code, 200)

    def test_exec_async_api(self):
        # APIを非同期実行するテスト
        response = self.client.post(
            self.BASE_URL + "api/exec_async/find_json_diff/", self.FIND_JSON_DIFF_DATA, "application/json")

        result = json.loads(response.content)

        result_id = result["result_id"]

        self.assertEqual(result_id, None)
        self.assertEqual(response.status_code, 200)
