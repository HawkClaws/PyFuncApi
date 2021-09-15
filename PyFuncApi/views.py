from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http.request import HttpRequest
import traceback
import json
from datetime import datetime
from .repository.repository import Repository
from .service.exec_service import *
from django.conf import settings

code_data_repository = Repository(settings.CODE_DATA_REPOSITORY_URL)

code_data_cache = {}

def get_code_data(url):
    if (url in code_data_cache.keys()) == False:
        code_data = json.loads(code_data_repository.select(url).text)
        if code_data == None:
            return code_data
        code_data_cache[url] = code_data
    return code_data_cache[url]


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


def logging(request: HttpRequest, url: str, body: str):
    try:
        repository = Repository(
            "https://animal-albums.firebaseio.com/6470E0696521449FB4FD1D36A4F87A80")

        repository.insert('', json.dumps({
            "url": url,
            "body": body,
            "client_addr": str(request.META.get('REMOTE_ADDR')),
            "datetime": str(datetime.now())
        }))
    except:
        pass


@csrf_exempt
def api_exec(request: HttpRequest, url: str):
    """
    登録済みAPIを同期実行します
    """
    try:
        input = request.body.decode('utf-8')
        logging(request, url, input)

        code = get_code_data(url)["code"]
        res = exec_wrapper(code, input)[HTTP_RESPONSE]
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

    result = ""
    if request.method.upper() == "GET":
        result = get_code_data(url)
    elif request.method.upper() == "POST":
        try:
            exists = get_code_data(url)
            if exists != None:
                return HttpResponse('URL that already exists', status=400)

            res_json = exec_wrapper(code)
            if res_json[IS_SUCCESS]:
                json_res = code_data_repository.update(
                    url, json.dumps(api_data)).text
                data = json.loads(str(json_res))
                data["result"] = res_json[HTTP_RESPONSE].content.decode(
                    'utf-8')
                result = json.dumps(data)
            elif res_json[IS_SUCCESS] == False:
                return res_json[HTTP_RESPONSE]
        except Exception as e:
            print(traceback.format_exc())
            return HttpResponse(e, status=400)
    elif request.method.upper() == "PUT":
        return HttpResponse("", status=501)
    elif request.method.upper() == "DELETE":
        return HttpResponse("", status=501)

    return HttpResponse(result)


def wakeup(request: HttpRequest):
    """
    djangoの起動を維持します
    """
    return HttpResponse("")
