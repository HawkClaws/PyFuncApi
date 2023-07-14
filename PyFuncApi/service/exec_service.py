from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http.request import HttpRequest
import threading
import traceback
import uuid

import json

from ..repository.instance_mongo_repository import get_async_data_repository
from ..service.common_function import to_json
from ..service.logging import logging, get_log_data, logging_with_merge, EXEC_TYPE, TRACE_ID
from django.conf import settings


# 外部からの入力
# EXEC_INPUT = 'exec_input'
# API実行結果
EXEC_RESULT = 'exec_result'

REQUEST = 'request'
RESPONSE = 'response'

TO_JSON = 'to_json'
RESILT_ID = "result_id"

HTTP_RESPONSE = "http_response"


def async_method(code: str, request: HttpRequest, url: str, result_id: str, exec_type: str, trace_id: str) -> HttpResponse:

    res = exec_wrapper(code, request)
    result_text = res.content.decode('utf-8')

    if res.status_code == 200:
        logging_with_merge(request, {"body": result_text}, {
                           TRACE_ID: trace_id, EXEC_TYPE: exec_type})
    else:
        logging_with_merge(request, {"body": result_text}, {
                           TRACE_ID: trace_id, EXEC_TYPE: exec_type}, "error")

    if result_id != None:
        get_async_data_repository().update(
            result_id, {"result": result_text, "status_code": res.status_code})
    return res


def exec_async_wrapper(code: str, request: HttpRequest, url: str, is_save_result: bool, trace_id: str) -> HttpResponse:
    """
    Pythonのコードを非同期実行します
    """
    result_id = None
    if is_save_result:
        result_id = str(uuid.uuid4())
    t1 = threading.Thread(target=async_method, args=(
        [code, request, url, result_id, "async_result", trace_id]))
    t1.start()
    return HttpResponse(json.dumps({"result_id": result_id}))


def exec_wrapper(code: str, request: HttpRequest) -> HttpResponse:
    """
    Pythonのコードを同期実行します
    """
    data = {}
    data[REQUEST] = request
    try:
        exec(code, data)
    except Exception as e:
        # TODO セキュリティ問題に気をつけること
        return HttpResponse(traceback.format_exc(), status=400)

    if RESPONSE in data.keys():
        return data[RESPONSE]

    # TODO EXEC_RESULTが必要かどうか再検討。
    if EXEC_RESULT in data.keys():
        return HttpResponse(data[EXEC_RESULT], status=200)
    else:
        return HttpResponse('Not Found exec_result data', status=400)


def api_exec_async_result(request: HttpRequest, result_id: str):
    """
    MongoDBから非同期実行の結果を取得します
    """
    result = get_async_data_repository(
    ).select_and_delete({'id': result_id})
    if result == None:
        # TODO 問答無用で202を返すのは良くなさそう。先にからの箱を作っておいてNoneと空でステータスコードを分ける等の実装が必要そう
        return HttpResponse('processing', status=202)

    res = HttpResponse(result["result"], status=result["status_code"])
    res['Content-Type'] = 'text/json'
    return res
