import pickle
from django.http import HttpRequest

def pickle_http_request(request: HttpRequest) -> bytes:
    data = {
        'method': request.method,
        'body': request.read(),
        'path': request.path,
    }
    return pickle.dumps(data)

def unpickle_http_request(pickled_request: bytes) -> HttpRequest:
    data = pickle.loads(pickled_request)
    request = HttpRequest()
    request.method = data['method']
    request._body = data['body']
    request.path = data['path']
    return request