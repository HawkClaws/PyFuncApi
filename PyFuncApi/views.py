import traceback
import json
import uuid
from datetime import datetime

from .service.http_request_serializer import pickle_http_request
from .repository.instance_mongo_repository import get_batch_task_repository
# from .service import import_service
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http.request import HttpRequest

from .service.api_crud_service import get_code_data, api_operation_service, delete_code_cache
from .service.logging import logging, logging_with_merge, EXEC_TYPE, TRACE_ID
from .service.exec_service import exec_async_wrapper, exec_wrapper, api_exec_async_result
from .service.authentication import authentication

@csrf_exempt
def api_exec_single(request: HttpRequest):
    """
    POSTされたPythonのコードを同期実行します
    """
    code = request.body.decode('utf-8')
    return exec_wrapper(code, request)


@csrf_exempt
def api_exec_async_single(request: HttpRequest, url: str):
    """
    POSTされたPythonのコードを非同期実行します
    """
    code = request.body.decode('utf-8')
    return exec_async_wrapper(code, request, url, False)


@csrf_exempt
def api_exec_single_with_input(request: HttpRequest):
    """
    POSTされたPythonのコードを同期実行します(inputあり)
    """
    data = json.loads(request.body.decode('utf-8'))
    code = data["code"]
    # input = data["input"]
    return exec_wrapper(code, request)


@csrf_exempt
def api_exec(request: HttpRequest, url: str):
    """
    登録済みAPIを同期実行します
    """
    try:
        logging(request, {EXEC_TYPE: "api_exec"})

        code_info = get_code_data(url)
        if code_info is None:
            return HttpResponse("Can not find api url:"+url)

        res = exec_wrapper(code_info["code"], request)
        if res.status_code != 200:
            logging_with_merge(
                request, {"body": res.content.decode('utf-8')}, {}, "error")

        if res['Content-Type'] == '':
            res['Content-Type'] = 'text/json'
        return res
    except Exception as e:
        print(traceback.format_exc())
        res = HttpResponse(e, status=400)
        res['Content-Type'] = 'text/json'
        return res


@csrf_exempt
def api_exec_async(request: HttpRequest, url: str, is_save_result: bool = False):
    """
    登録済みAPIを非同期実行します
    """
    try:
        trace_id = str(uuid.uuid4())
        logging(request, {EXEC_TYPE: "api_exec_async", TRACE_ID: trace_id})

        code_info = get_code_data(url)
        if code_info is None:
            return HttpResponse("Can not find api url:"+url)

        res = exec_async_wrapper(
            code_info["code"], request, url, is_save_result, trace_id)
        return res
    except Exception as e:
        print(traceback.format_exc())
        res = HttpResponse(e, status=400)
        res['Content-Type'] = 'text/json'
        return res


@csrf_exempt
def api_exec_async_save(request: HttpRequest, url: str):
    """
    登録済みAPIを非同期実行し、結果保存します
    """
    return api_exec_async(request, url, True)


@csrf_exempt
def exec_batch(request: HttpRequest, url: str, is_save_result: bool = False):
    """
    登録済みAPIをバッチ実行登録します
    """
    try:
        trace_id = str(uuid.uuid4())
        logging(request, {EXEC_TYPE: "batch_register", TRACE_ID: trace_id})

        code_info = get_code_data(url)
        if code_info is None:
            return HttpResponse("Can not find api url:"+url)

        result_id = None
        if is_save_result:
            result_id = str(uuid.uuid4())

        get_batch_task_repository().insert({
            "created_at": datetime.now(),
            "http_request_data": pickle_http_request(request),
            "url": url,
            "result_id": result_id,
            "trace_id": trace_id,
        })

        return HttpResponse(json.dumps({"result_id": result_id}, ensure_ascii=False))
    except Exception as e:
        print(traceback.format_exc())
        res = HttpResponse(e, status=400)
        res['Content-Type'] = 'text/json'
        return res


@csrf_exempt
def exec_batch_save(request: HttpRequest, url: str):
    """
    登録済みAPIを非同期実行し、結果保存します
    """
    return exec_batch(request, url, True)


@csrf_exempt
def api_operation_nocheck(request: HttpRequest, url: str):
    """
    APIの情報を登録等の操作をします(APIは実行しない)
    """
    return api_operation_common(request, url, False)


@csrf_exempt
def api_operation(request: HttpRequest, url: str):
    """
    APIの情報を登録等の操作をします
    """
    return api_operation_common(request, url, True)


def api_operation_common(request: HttpRequest, url: str, check_code: bool):
    """
    APIの情報を登録等の操作をします
    """

    authorization = request.META.get('HTTP_AUTHORIZATION')
    if not authentication(authorization):
        return HttpResponse("Authentication failed", status=401)

    code = request.body.decode('utf-8')
    logging(request, {EXEC_TYPE: "api_operation"} if check_code else {
            EXEC_TYPE: "api_operation_nocheck"})

    api_data = {
        "url": url,
        "code": code
    }

    return api_operation_service(api_data, request.method.upper(), check_code)


@csrf_exempt
def refresh_cache(request: HttpRequest):
    delete_code_cache()
    return HttpResponse("refresh_cached")


def wakeup(request: HttpRequest):
    """
    djangoの起動を維持します
    """
    return HttpResponse("Awaked!")


# def import_modules(request: HttpRequest):
#     return import_service.inport_module()
