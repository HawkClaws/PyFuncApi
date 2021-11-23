from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http.request import HttpRequest
import traceback
from .service.api_crud_service import api_operation_common, get_code_data
from .service.logging import logging
from .service.exec_service import exec_async_wrapper, exec_wrapper, api_exec_async_result, HTTP_RESPONSE


@csrf_exempt
def api_exec_single(request: HttpRequest):
    """
    POSTされたPythonのコードを同期実行します
    """
    code = request.body.decode('utf-8')
    return exec_wrapper(code)[HTTP_RESPONSE]


@csrf_exempt
def api_exec_async_single(request: HttpRequest):
    """
    POSTされたPythonのコードを非同期実行します
    """
    code = request.body.decode('utf-8')
    return exec_async_wrapper(code)


@csrf_exempt
def api_exec(request: HttpRequest, url: str):
    """
    登録済みAPIを同期実行します
    """
    try:
        input = request.body.decode('utf-8')
        logging(request, url, input)

        code_info = get_code_data(url)
        if code_info is None:
            return HttpResponse("Can not find api url:"+url)

        res = exec_wrapper(code_info["code"], input)[HTTP_RESPONSE]
        res['Content-Type'] = 'text/json'
        return res
    except Exception as e:
        print(traceback.format_exc())
        res = HttpResponse(e, status=400)
        res['Content-Type'] = 'text/json'
        return res


@csrf_exempt
def api_exec_async(request: HttpRequest, url: str):
    """
    登録済みAPIを非同期実行します
    """
    try:
        input = request.body.decode('utf-8')
        logging(request, url, input)

        code = get_code_data(url)["code"]
        res = exec_async_wrapper(code, input)
        return res
    except Exception as e:
        print(traceback.format_exc())
        res = HttpResponse(e, status=400)
        res['Content-Type'] = 'text/json'
        return res


@csrf_exempt
def api_operation_nocheck(request: HttpRequest, url: str):
    """
    APIの情報を登録等の操作をします(APIは実行しない)
    """
    code = request.body.decode('utf-8')
    logging(request, url, code)
    # json_object = json.loads(result)

    api_data = {}
    api_data["url"] = url
    api_data["code"] = code
    # api_data["pass"] = json_object["pass"]

    return api_operation_common(api_data, request.method.upper(), False)


@csrf_exempt
def api_operation(request: HttpRequest, url: str):
    """
    APIの情報を登録等の操作をします
    """
    code = request.body.decode('utf-8')
    logging(request, url, code)
    # json_object = json.loads(result)

    api_data = {}
    api_data["url"] = url
    api_data["code"] = code
    # api_data["pass"] = json_object["pass"]

    return api_operation_common(api_data, request.method.upper(), True)


def wakeup(request: HttpRequest):
    """
    djangoの起動を維持します
    """
    return HttpResponse("")
