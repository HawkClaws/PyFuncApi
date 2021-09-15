import requests
import numpy as np
from datetime import datetime
import json
import time


def request_extend(method, url, body, headers):
    res = requests.request(method, url=url,
                           data=body, headers=headers)
    encoding = res.apparent_encoding
    if not encoding == 'Windows-1254' and res.encoding == 'Windows-1254':
        res.encoding = encoding
    elif encoding == 'utf-8':
        res.encoding = 'Unicode'
    return res


def add_key():
    return np.base_repr(int(datetime.now().strftime('%Y%m%d%H%M%S%f')), 36)


def to_json(text: str, use_key=False):
    json_object = {}
    is_json = False
    try:
        json_obj_temp = json.loads(text)
        if isinstance(json_obj_temp,list):
            for obj in json_obj_temp:
                time.sleep(0.000001)
                json_object[add_key()] = obj
        else:
            json_object = json_obj_temp
        is_json = True
    except:
        pass

    if is_json == False:
        json_object = {"value": text}

    if use_key == True:
        json_object["_key"] = add_key()

    return json.dumps(json_object, ensure_ascii=False)
