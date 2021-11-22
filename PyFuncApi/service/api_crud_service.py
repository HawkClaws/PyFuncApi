from types import TracebackType
from ..repository.repository import Repository
from ..service.exec_service import *

code_data_cache = {}
code_data_repository = Repository(settings.CODE_DATA_REPOSITORY_URL)

def api_operation_common(api_data, method, check):
    """
    APIの情報を登録等の操作をします
    """
    result = ""
    if method == "GET":
        result = get_code_data(api_data["url"])
    elif method == "POST":
        try:
            exists = get_code_data(api_data["url"])
            if exists != None:
                return HttpResponse('URL that already exists', status=400)

            res_json = {IS_SUCCESS: True,
                        HTTP_RESPONSE: HttpResponse("No Check")}
            if check == True:
                res_json = exec_wrapper(api_data["url"])
            
            if res_json[IS_SUCCESS]:
                json_res = code_data_repository.update(
                    api_data["url"], json.dumps(api_data)).text
                data = json.loads(str(json_res))
                data["result"] = res_json[HTTP_RESPONSE].content.decode(
                    'utf-8')
                result = json.dumps(data)
            elif res_json[IS_SUCCESS] == False:
                return res_json[HTTP_RESPONSE]
        except Exception as e:
            print(TracebackType.format_exc())
            return HttpResponse(e, status=400)
    elif method == "PUT":
        return HttpResponse("", status=501)
    elif method == "DELETE":
        return HttpResponse("", status=501)

    return HttpResponse(result)


def get_code_data(url):
    if (url in code_data_cache.keys()) == False:
        code_data = json.loads(code_data_repository.select(url).text)
        if code_data == None:
            return code_data
        code_data_cache[url] = code_data
    return code_data_cache[url]
