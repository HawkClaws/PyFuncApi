import traceback
from django.http.request import HttpRequest
from ..repository.repository import Repository
import json
from datetime import datetime

from django.conf import settings


def logging(request: HttpRequest, url: str, body: str):
    try:
        repository = Repository(
            settings.LOGGING_REPOSITORY_URL)
        now = datetime.now()
        hour = now.strftime("%Y-%m-%d")
        minute = now.strftime("%H:%M:%S")
        
        forwarded_addresses = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_addresses:
            # 'HTTP_X_FORWARDED_FOR'ヘッダがある場合: 転送経路の先頭要素を取得する。
            client_addr = forwarded_addresses.split(',')[0]
        else:
            # 'HTTP_X_FORWARDED_FOR'ヘッダがない場合: 直接接続なので'REMOTE_ADDR'ヘッダを参照する。
            client_addr = request.META.get('REMOTE_ADDR')

        path = '/'.join([url,request.method, hour, minute])
        repository.update(path, json.dumps({
            "url": url,
            "body": body,
            "client_addr": str(client_addr),
            "datetime": str(datetime.now())
        }))
    except Exception as e:
        print(traceback.format_exc())
        pass