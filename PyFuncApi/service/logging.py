from django.http.request import HttpRequest
from ..repository.repository import Repository
import json
from datetime import datetime

from django.conf import settings


def logging(request: HttpRequest, url: str, body: str):
    try:
        repository = Repository(
            settings.LOGGING_REPOSITORY_URL)

        repository.insert('', json.dumps({
            "url": url,
            "body": body,
            "client_addr": str(request.META.get('REMOTE_ADDR')),
            "datetime": str(datetime.now())
        }))
    except:
        pass