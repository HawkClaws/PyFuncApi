from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http.request import HttpRequest
import threading
import uuid
import json
from ..repository.repository import Repository
from ..service.common_function import to_json
from django.conf import settings

async_data_repository = Repository(settings.ASYNC_DATA_REPOSITORY_URL)
# 外部からの入力
EXEC_INPUT = 'exec_input'
# API実行結果
EXEC_RESULT = 'exec_result'
ASYNC_REPOSITORY = 'async_data_repository'
EXEC_RESULT_STATUS = 'exec_result_status'

TO_JSON = 'to_json'
RESILT_ID = "result_id"

HTTP_RESPONSE = "http_response"
IS_SUCCESS = "is_success"

def exec_async_wrapper(code, input=""):
    """
    Pythonのコードを非同期実行します
    """
    result_id = str(uuid.uuid4())

    # 非同期の実行結果を保存する
    code = code + '\nasync_data_repository.update(result_id,to_json(exec_result))'
    # code = code + '\nprint(async_data_repository.update(result_id,to_json(exec_result)).text)'
    # code = code + '\nprint(to_json(exec_result))'
    ref_data = {}

    # api_exec_async_data[result_id] = ref_data
    ref_data[EXEC_INPUT] = input
    ref_data[EXEC_RESULT] = {}
    ref_data[ASYNC_REPOSITORY] = async_data_repository
    ref_data[RESILT_ID] = result_id
    ref_data[TO_JSON] = to_json
    t1 = threading.Thread(target=exec, args=([code, ref_data]))
    t1.start()
    return HttpResponse(json.dumps({RESILT_ID: result_id}))


def exec_wrapper(code, input="", repository={}):
    """
    Pythonのコードを同期実行します
    """
    data = {}
    data[EXEC_INPUT] = input
    try:
        exec(code, data)
    except Exception as e:
        print(e.args)
        return {HTTP_RESPONSE: HttpResponse(e.args, status=400), IS_SUCCESS: False}

    status_code = 200
    if EXEC_RESULT_STATUS in data.keys():
        status_code = data[EXEC_RESULT_STATUS]

    if EXEC_RESULT in data.keys():
        return {HTTP_RESPONSE: HttpResponse(data[EXEC_RESULT], status=status_code), IS_SUCCESS: True}
    else:
        return {HTTP_RESPONSE: HttpResponse('Not Found exec_result data', status=400), IS_SUCCESS: True}


def api_exec_async_result(request: HttpRequest, result_id: str):
    """
    非同期実行の結果を取得します
    """
    result = async_data_repository.select(result_id).text
    if result == 'null':
        return HttpResponse('Not Found result_id', status=404)
    async_data_repository.delete(result_id)
    res = HttpResponse(result)
    res['Content-Type'] = 'text/json'
    return res
    

# def api_exec_async_result(request: HttpRequest, result_id: str):
#     """
#     非同期実行の結果を取得します
#     """
#     if result_id in api_exec_async_data.keys():
#         log_data = api_exec_async_data[result_id]
#         if EXEC_RESULT in log_data.keys():
#             ret_data = log_data[EXEC_RESULT]
#             del api_exec_async_data[result_id]
#             return HttpResponse(ret_data)
#         else:
#             return HttpResponse('Not Found exec_result', status=404)
#     else:
#         return HttpResponse('Not Found result_id', status=404)
