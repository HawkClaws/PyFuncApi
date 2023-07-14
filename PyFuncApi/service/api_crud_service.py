import json
import traceback
from django.shortcuts import HttpResponse
from ..service.exec_service import exec_wrapper
from ..repository.instance_mongo_repository import get_api_data_repository

code_data_cache = {}


def delete_code_cache():
    global code_data_cache
    code_data_cache = {}


def api_operation_service(api_data, method, check):
    """
    APIの情報を登録等の操作をします
    """
    result = ""
    if method == "GET":
        result = get_code_data(api_data["url"])
        result = result["code"]
    elif method == "POST":
        try:
            # キャッシュをクリアする
            exists = get_code_data(api_data["url"], cache=False)
            if exists != None:
                return HttpResponse('URL that already exists', status=400)

            res = HttpResponse("No Check")
            if check == True:
                # TODO Check必要？再検討。
                res = exec_wrapper(api_data["url"])
            if res.status_code == 200:  # TODO 200のみでOK？再検討。
                json_res = get_api_data_repository().update(
                    api_data["url"], api_data)
                data = json_res.raw_result

                del data["upserted"]
                data["result"] = res.content.decode(
                    'utf-8')
                result = json.dumps(data)
            else:
                return res
        except Exception as e:
            print(traceback.format_exc())
            return HttpResponse(e, status=400)
    elif method == "PUT":
        return HttpResponse("", status=501)
    elif method == "DELETE":
        return HttpResponse("", status=501)

    return HttpResponse(result)


def get_code_data(url, cache=True):
    global code_data_cache
    if (url in code_data_cache.keys()) == False or cache == False:
        code_data = get_api_data_repository().select({"id": url})
        if code_data == None:
            code_data_cache.pop(url, None)
            return code_data
        code_data_cache[url] = code_data
    return code_data_cache[url]
