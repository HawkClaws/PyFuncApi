import traceback
from django.http.request import HttpRequest
import json
from datetime import datetime
from typing import Union, overload

from django.conf import settings
from datadog import initialize, api


EXEC_TYPE = "exec_type"
TRACE_ID = "trace_id"

datadog_api = None


def initialize_datadog():
    global datadog_api
    if settings.DATADOG_API_KEY is None or settings.DATADOG_APP_KEY is None:
        # DATADOG_API_KEYまたはDATADOG_APP_KEYがNoneの場合、ログを標準出力に出力する
        return None
    else:
        options = {
            "api_key": settings.DATADOG_API_KEY,
            "app_key": settings.DATADOG_APP_KEY,
        }
        initialize(**options)
        datadog_api = api
        return datadog_api


def get_log_data(request: HttpRequest) -> dict:
    forwarded_addresses = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_addresses:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがある場合: 転送経路の先頭要素を取得する。
        client_addr = forwarded_addresses.split(',')[0]
    else:
        # 'HTTP_X_FORWARDED_FOR'ヘッダがない場合: 直接接続なので'REMOTE_ADDR'ヘッダを参照する。
        client_addr = request.META.get('REMOTE_ADDR')

    return {
        "body": request.body.decode('utf-8'),
        "url": request.path,
        "client_addr": str(client_addr),
        "host": request.META.get('HTTP_HOST')
    }


@overload
def logging(request: HttpRequest, tag_data: dict, alert_type: str = "info"):
    ...


@overload
def logging(log_data: dict, tag_data: dict, alert_type: str = "info"):
    ...


def logging_with_merge(request: HttpRequest, update_log_data: dict, tag_data: dict, alert_type: str = "info"):
    log_data = get_log_data(request)
    log_data.update(update_log_data)
    logging(log_data, tag_data, alert_type)


def logging(log_data: Union[HttpRequest, dict], tag_data: dict, alert_type: str = "info"):
    if isinstance(log_data, HttpRequest):
        logging_common(get_log_data(log_data), tag_data, alert_type)
    elif isinstance(log_data, dict):
        logging_common(log_data, tag_data, alert_type)
    else:
        logging_common({"error": "bad type"}, tag_data, alert_type)


def logging_common(log_data: dict, tag_data: dict, alert_type: str = "info"):
    try:
        global datadog_api
        if 'url' not in log_data:
            print("log_dataにurlが見つかりません")
            log_data["url"] = "url_dummy"

        tag_data["app"] = "PyFuncApi"
        tag_data["url"] = log_data["url"]
        if 'host' in log_data:
            tag_data["host"] = log_data["host"]

        tags = []
        for key in tag_data.keys():
            tags.append(f"{key}:{tag_data[key]}")

        log_data["datetime"] = str(datetime.now())
        title = log_data["url"]

        text = json.dumps(log_data, ensure_ascii=False)

        if datadog_api is None:
            datadog_api = initialize_datadog()

        if datadog_api is not None:
            datadog_api.Event.create(
                title=title, text=text, tags=tags, alert_type=alert_type)
        else:
            # Datadogが利用できない場合、ログを標準出力に出力する
            print(f"Logging - Title: {title}, Text: {text}, Tags: {tags}")
    except Exception as e:
        print(traceback.format_exc())
        pass
